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
    cache_path = LICENSE_DIR / CACHE_FILE
    cache_path.touch()

    return {"status": "ok", "customer_id": customer_id}


def revoke_license() -> dict:
    """Remove local license and cache files."""
    license_path = LICENSE_DIR / LICENSE_FILE
    cache_path = LICENSE_DIR / CACHE_FILE

    license_path.unlink(missing_ok=True)
    cache_path.unlink(missing_ok=True)

    return {"status": "ok", "message": "License revoked."}


def is_license_valid() -> bool:
    """Check if a valid, non-expired license exists locally.

    Returns True only if both license.json exists AND the cache
    file is less than 24 hours old. When cache expires, the caller
    should re-validate via Stripe API and touch the cache.
    """
    license_path = LICENSE_DIR / LICENSE_FILE
    cache_path = LICENSE_DIR / CACHE_FILE

    if not license_path.exists():
        return False

    if not cache_path.exists():
        return False

    # Check cache age
    cache_age = time.time() - cache_path.stat().st_mtime
    if cache_age > CACHE_TTL:
        return False

    return True


def cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point for license management.

    Usage:
        atlas-license activate <customer_id>
        atlas-license revoke
        atlas-license status
    """
    import sys

    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("Usage: atlas-license {activate,revoke,status}")
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

    print(f"Unknown command: {command}")
    return 1


def _cli_entry() -> None:
    """Entry point for project.scripts — wraps cli_main with sys.exit."""
    import sys

    sys.exit(cli_main())


if __name__ == "__main__":
    _cli_entry()
