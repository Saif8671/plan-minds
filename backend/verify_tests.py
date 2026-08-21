import asyncio
import httpx
from httpx import ASGITransport

async def run_verification():
    # Import app here so we can run it with no ENVIRONMENT set
    import os
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
    
    from main import app
    from app.core.config import get_settings
    
    # Assert environment is now production
    assert get_settings().environment == "production"

    print("--- Item 2 Verification ---")
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a user first
        await client.post("/api/v1/auth/register", json={
            "email": "verify2@example.com",
            "password": "Password123!",
            "name": "Verify 2"
        })
        
        # Call forgot password
        resp = await client.post("/api/v1/auth/forgot-password", json={"email": "verify2@example.com"})
        print(f"Forgot password response ({resp.status_code}): {resp.json()}")
        
    print("\n--- Item 3 Verification ---")
    # Make sure Redis is pointed to a dead port
    os.environ["REDIS_URL"] = "redis://localhost:9999"
    import app.core.redis as redis_core
    if redis_core.redis_client:
        await redis_core.close_redis()
        redis_core.redis_client = None

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # register
        reg = await client.post("/api/v1/auth/register", json={
            "email": "verify3@example.com",
            "password": "Password123!",
            "name": "Verify 3"
        })
        print(f"Register: {reg.status_code}")
        
        # login
        log = await client.post("/api/v1/auth/login", json={
            "email": "verify3@example.com",
            "password": "Password123!"
        })
        print(f"Login: {log.status_code}")
        token = log.json()["data"]["access_token"]
        
        # forgot-password
        forgot = await client.post("/api/v1/auth/forgot-password", json={"email": "verify3@example.com"})
        print(f"Forgot password: {forgot.status_code}")
        
        # Wait, how do I get the OTP? Since I'm not in development mode, OTP is not returned!
        # Ah! I need to manually get the OTP from the database.
        from app.core.database import TestSessionLocal if 'TestSessionLocal' in globals() else get_db
        # Actually I can just switch to development mode for this part to get the OTP, 
        # or grab it from DB. Let's just grab it from DB.
        
if __name__ == "__main__":
    asyncio.run(run_verification())
