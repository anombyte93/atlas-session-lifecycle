"""Tests for Stripe integration."""

from unittest.mock import MagicMock, patch

import pytest

from atlas_session.stripe_client import (
    StripeNotConfigured,
    StripeSignatureError,
    create_checkout_session,
    handle_checkout_completed,
    is_stripe_configured,
    refresh_local_license,
    verify_webhook_signature,
)


class TestStripeConfiguration:
    """Tests for Stripe configuration detection."""

    def test_is_stripe_configured_no_key(self, monkeypatch):
        """Returns False when STRIPE_SECRET_KEY is not set."""
        monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
        assert not is_stripe_configured()

    def test_is_stripe_configured_with_key(self, monkeypatch):
        """Returns True when STRIPE_SECRET_KEY is set."""
        monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")
        assert is_stripe_configured()


class TestCreateCheckoutSession:
    """Tests for checkout session creation."""

    def test_create_checkout_no_key_raises(self, monkeypatch):
        """Raises StripeNotConfigured when no API key."""
        monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)

        with pytest.raises(StripeNotConfigured):
            create_checkout_session(
                customer_email="test@example.com",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    @patch("atlas_session.stripe_client.stripe")
    def test_create_checkout_success(self, mock_stripe, monkeypatch):
        """Creates checkout session successfully."""
        monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")
        monkeypatch.setenv("STRIPE_PRICE_MONTHLY_ID", "price_monthly")

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/pay/123"
        mock_session.id = "cs_test_123"

        mock_stripe.checkout.Session.create.return_value = mock_session

        result = create_checkout_session(
            customer_email="test@example.com",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        assert result["status"] == "ok"
        assert "checkout_url" in result
        assert result["session_id"] == "cs_test_123"


class TestWebhookSignature:
    """Tests for webhook signature verification."""

    def test_verify_webhook_no_signature(self, monkeypatch):
        """Raises error when signature header is missing."""
        monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)

        with pytest.raises(StripeSignatureError):
            verify_webhook_signature(b"{}", "")

    @patch("atlas_session.stripe_client.stripe")
    def test_verify_webhook_invalid_signature(self, mock_stripe, monkeypatch):
        """Raises error for invalid signature."""
        monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_123")
        monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")

        class SignatureVerificationError(Exception):
            pass

        mock_stripe.error = MagicMock()
        mock_stripe.error.SignatureVerificationError = SignatureVerificationError
        mock_stripe.Webhook.construct_event.side_effect = SignatureVerificationError("Invalid signature")

        with pytest.raises(StripeSignatureError):
            verify_webhook_signature(b"{}", "t=123,v1=bad")

    @patch("atlas_session.stripe_client.stripe")
    def test_verify_webhook_success(self, mock_stripe, monkeypatch):
        """Verifies valid webhook signature."""
        monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_123")
        monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")

        mock_event = MagicMock()
        mock_event.type = "checkout.session.completed"
        mock_event.data = {"object": {"customer": "cus_123"}}

        mock_stripe.Webhook.construct_event.return_value = mock_event

        result = verify_webhook_signature(b"payload", "t=123,v1=valid")

        assert result["status"] == "ok"
        assert result["event_type"] == "checkout.session.completed"


class TestHandleCheckoutCompleted:
    """Tests for checkout completion handling."""

    def test_handle_checkout_activates_license(self, tmp_path, monkeypatch):
        """Activates license when checkout completes."""
        monkeypatch.setenv("ATLAS_LICENSE_DIR", str(tmp_path))

        session_data = {
            "object": {
                "customer": "cus_123",
                "customer_details": {"email": "test@example.com"},
            }
        }

        result = handle_checkout_completed(session_data)

        assert result["status"] == "ok"
        assert "customer_id" in result

        # Verify license file was created
        license_file = tmp_path / "license.json"
        assert license_file.exists()


class TestRefreshLicense:
    """Tests for license refresh from Stripe."""

    def test_refresh_no_customer_id(self, tmp_path, monkeypatch):
        """Returns error when license has no customer_id."""
        monkeypatch.setenv("ATLAS_LICENSE_DIR", str(tmp_path))

        # Create license without customer_id
        license_file = tmp_path / "license.json"
        license_file.write_text('{"status": "active"}')

        result = refresh_local_license()

        # Should return error since no customer_id to validate
        assert result["status"] in ("error", "inactive")
