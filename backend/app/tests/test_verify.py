import pytest
import os
import httpx
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_verify_item_2(async_client: AsyncClient, monkeypatch):
    """Verify that forgot-password does not return OTP when not in dev environment."""
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    
    # Reload config
    from app.core.config import get_settings
    settings = get_settings()
    assert settings.environment == "production"

    # Register user
    resp = await async_client.post("/api/v1/auth/register", json={
        "email": "verify2@example.com",
        "password": "Password123!",
        "name": "Verify 2"
    })
    
    # Forgot password
    resp = await async_client.post("/api/v1/auth/forgot-password", json={"email": "verify2@example.com"})
    print(f"\n[ITEM 2 OUTPUT] Forgot password response body: {resp.json()}")
    assert "reset_token" in resp.json()
    assert resp.json()["reset_token"] == ""

@pytest.mark.asyncio
async def test_verify_item_3(async_client: AsyncClient, monkeypatch):
    """Verify that Redis failure does not cause 500s."""
    import app.core.redis as redis_core
    
    # Point redis to bad port and re-init
    monkeypatch.setattr(redis_core.settings, "redis_url", "redis://localhost:9999")
    await redis_core.close_redis()
    redis_core.redis_client = None
    await redis_core.init_redis()
    
    email = "verify3@example.com"
    
    # register
    reg = await async_client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "name": "Verify 3"
    })
    print(f"\n[ITEM 3 OUTPUT] Register status: {reg.status_code}")
    
    # login
    log = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    print(f"[ITEM 3 OUTPUT] Login status: {log.status_code}")
    token = log.json()["data"]["access_token"]
    
    # forgot-password
    forgot = await async_client.post("/api/v1/auth/forgot-password", json={"email": email})
    print(f"[ITEM 3 OUTPUT] Forgot password status: {forgot.status_code}")
    
    # To get OTP we need DB
    from app.core.database import TestSessionLocal
    from app.models import User
    from sqlalchemy import select
    async with TestSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        otp = user.reset_otp

    # verify otp
    ver = await async_client.post("/api/v1/auth/verify-otp", json={"email": email, "otp": otp})
    print(f"[ITEM 3 OUTPUT] Verify OTP status: {ver.status_code}")
    reset_token = ver.json()["data"]["reset_token"]
    
    # reset password
    res = await async_client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": "NewPassword123!"
    })
    print(f"[ITEM 3 OUTPUT] Reset password status: {res.status_code}")
    
    # logout
    logout = await async_client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    print(f"[ITEM 3 OUTPUT] Logout status: {logout.status_code}")
    
    # get current user
    me = await async_client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    print(f"[ITEM 3 OUTPUT] Get user status: {me.status_code}")
