from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_forgot_password_flow(async_client: AsyncClient):
    # Register a user first
    register_resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "forgot@example.com",
            "password": "OldPassword123!",
            "name": "Forgot User",
        },
    )
    assert register_resp.status_code == 201

    # Force production mode to ensure OTP isn't leaked
    from app.core.config import get_settings

    settings = get_settings()
    settings.environment = "production"

    # Mock EmailService to capture the OTP
    with patch("app.services.email_service.EmailService.send_email") as mock_send_email:
        mock_send_email.return_value = True

        # 1. POST forgot-password
        forgot_resp = await async_client.post(
            "/api/v1/auth/forgot-password", json={"email": "forgot@example.com"}
        )
        assert forgot_resp.status_code == 200
        data = forgot_resp.json()
        assert data["data"]["reset_token"] == ""  # Should not return token in body

        # Get OTP from mock call
        assert mock_send_email.called
        call_args = mock_send_email.call_args[1]
        assert call_args["to_email"] == "forgot@example.com"

        # Extract OTP from body
        body = call_args["body"]
        otp = [
            word
            for word in body.replace(".", "").replace(":", "").split()
            if word.isdigit() and len(word) == 6
        ][0]

    # 2. Verify OTP
    verify_resp = await async_client.post(
        "/api/v1/auth/verify-otp", json={"email": "forgot@example.com", "otp": otp}
    )
    assert verify_resp.status_code == 200
    reset_token = verify_resp.json()["data"]["reset_token"]
    assert reset_token != ""

    # 3. Reset password
    reset_resp = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "password": "NewPassword123!"},
    )
    assert reset_resp.status_code == 200

    # 4. Login with old password (must 401)
    login_old = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "forgot@example.com", "password": "OldPassword123!"},
    )
    assert login_old.status_code == 401

    # 5. Login with new password (must 200)
    login_new = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "forgot@example.com", "password": "NewPassword123!"},
    )
    assert login_new.status_code == 200
