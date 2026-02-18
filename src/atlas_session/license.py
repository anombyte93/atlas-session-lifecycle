"""License management for atlas-session-lifecycle Pro.

Handles local license activation, revocation, and cached validation.
Stripe API calls are only made when cache expires (every 24h).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

LICENSE_DIR = Path.home() / ".atlas-session"
LICENSE_FILE = "license.json"
CACHE_FILE = ".license_cache"
CACHE_TTL = 86400  # 24 hours


def _touch_cache() -> None:
    """Touch the cache file to mark license as freshly validated."""
    cache_path = LICENSE_DIR / CACHE_FILE
    cache_path.touch()


def _get_customer_id() -> str | None:
    """Read customer_id from license file if exists."""
    license_path = LICENSE_DIR / LICENSE_FILE
    if not license_path.exists():
        return None
    try:
        data = json.loads(license_path.read_text())
        return data.get("customer_id")
    except (json.JSONDecodeError, OSError):
        return None


def activate_license(customer_id: str) -> dict:
    """Activate a license by writing customer_id to license.json."""
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    license_path = LICENSE_DIR / LICENSE_FILE

    data = {
        "customer_id": customer_id,
        "activated_at": time.time(),
    }
    license_path.write_text(json.dumps(data, indent=2))

    # Touch cache to mark as freshly validated
    _touch_cache()

    return {"status": "ok", "customer_id": customer_id}


def revoke_license() -> dict:
    """Remove local license and cache files."""
    license_path = LICENSE_DIR / LICENSE_FILE
    cache_path = LICENSE_DIR / CACHE_FILE

    license_path.unlink(missing_ok=True)
    cache_path.unlink(missing_ok=True)

    return {"status": "ok", "message": "License revoked."}


def is_license_valid(refresh: bool = True) -> bool:
    """Check if a valid, non-expired license exists locally.

    Returns True only if both license.json exists AND the cache
    file is less than 24 hours old. When cache expires and refresh=True,
    attempts to re-validate via Stripe API.

    Args:
        refresh: If True, try Stripe validation when cache expired.

    Returns:
        True if license is valid (locally or after Stripe refresh), False otherwise.
    """
    license_path = LICENSE_DIR / LICENSE_FILE
    cache_path = LICENSE_DIR / CACHE_FILE

    if not license_path.exists():
        return False

    if not cache_path.exists():
        # Cache missing - try to refresh if requested
        if refresh:
            return _try_refresh_from_stripe()
        return False

    # Check cache age
    cache_age = time.time() - cache_path.stat().st_mtime
    if cache_age > CACHE_TTL:
        # Cache expired - try to refresh if requested
        if refresh:
            return _try_refresh_from_stripe()
        return False

    return True


def _try_refresh_from_stripe() -> bool:
    """Attempt to refresh license from Stripe API.

    Returns True if validation succeeded and cache was touched,
    False otherwise. Silently fails if Stripe is not configured.
    """
    customer_id = _get_customer_id()
    if not customer_id:
        return False

    try:
        from .stripe_client import validate_license_with_stripe

        result = validate_license_with_stripe(customer_id)
        if result.get("status") == "active":
            _touch_cache()
            return True
    except Exception:
        # Stripe not configured or API error - fail silently
        pass

    return False


def refresh_license() -> dict:
    """Manually refresh license from Stripe API.

    Forces validation with Stripe regardless of cache age.
    Useful when user wants to extend their license early.

    Returns:
        dict with status and validation result.
    """
    customer_id = _get_customer_id()
    if not customer_id:
        return {"status": "error", "message": "No local license found"}

    try:
        from .stripe_client import validate_license_with_stripe

        result = validate_license_with_stripe(customer_id)
        if result.get("status") == "active":
            _touch_cache()
            return {
                "status": "ok",
                "message": "License refreshed successfully",
                "license_type": result.get("type"),
            }
        return {
            "status": "inactive",
            "message": result.get("message", "License not active in Stripe"),
        }
    except ImportError:
        return {"status": "error", "message": "Stripe integration not available"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point for license management.

    Usage:
        atlas-license activate <customer_id>
        atlas-license revoke
        atlas-license status
        atlas-license refresh
    """
    import sys

    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("Usage: atlas-license {activate,revoke,status,refresh}")
        return 1

    command = argv[0]

    if command == "activate":
        if len(argv) < 2:
            print("Usage: atlas-license activate <customer_id>")
            return 1
        result = activate_license(argv[1])
        print(f"License activated for {result['customer_id']}")
        return 0

    if command == "revoke":
        revoke_license()
        print("License revoked.")
        return 0

    if command == "status":
        if is_license_valid():
            license_path = LICENSE_DIR / LICENSE_FILE
            data = json.loads(license_path.read_text())
            print(f"License: VALID (customer: {data.get('customer_id', 'unknown')})")
            return 0
        print("License: INVALID or expired")
        return 1

    if command == "refresh":
        result = refresh_license()
        if result.get("status") == "ok":
            print(f"License refreshed: {result.get('message', 'Success')}")
            return 0
        print(f"Refresh failed: {result.get('message', 'Unknown error')}")
        return 1

    print(f"Unknown command: {command}")
    return 1


def _cli_entry() -> None:
    """Entry point for project.scripts — wraps cli_main with sys.exit."""
    import sys

    sys.exit(cli_main())


if __name__ == "__main__":
    _cli_entry()
