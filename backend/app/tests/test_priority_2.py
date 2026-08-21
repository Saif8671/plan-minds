import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_logout_revocation_flow(async_client: AsyncClient):
    # Mock Redis methods
    mock_redis = AsyncMock()
    # Simple in-memory dict for the mock redis
    store = {}
    
    async def mock_exists(key):
        return 1 if key in store else 0
        
    async def mock_setex(key, ttl, value):
        store[key] = value
        
    async def mock_get(key):
        return store.get(key)
        
    mock_redis.exists.side_effect = mock_exists
    mock_redis.setex.side_effect = mock_setex
    mock_redis.get.side_effect = mock_get

    with patch("app.core.redis.get_redis", return_value=mock_redis):
        # Register a user
        register_resp = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "logout@example.com",
                "password": "Password123!",
                "name": "Logout User",
            },
        )
        assert register_resp.status_code == 201
        
        # Login
        login_resp = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "logout@example.com", "password": "Password123!"}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["data"]["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check /users/me works BEFORE logout
        # The app has a /users/me route in router.py maybe? Let's check api. 
        # For this test, we can just hit /api/v1/auth/logout which also requires token, but let's test a protected route if it exists.
        # Let's hit /api/v1/auth/logout with token
        logout_resp = await async_client.post(
            "/api/v1/auth/logout",
            headers=headers
        )
        assert logout_resp.status_code == 200
        
        # Now try to hit logout again, should fail with 401
        logout_resp_2 = await async_client.post(
            "/api/v1/auth/logout",
            headers=headers
        )
        assert logout_resp_2.status_code == 401, f"Expected 401, got {logout_resp_2.status_code}"
        
        print("SUCCESS! Token revocation works.")
