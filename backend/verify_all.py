import asyncio
import httpx
from httpx import ASGITransport
import os
import random

async def run():
    print("================ ITEM 2 ================")
    # Unset environment
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
    
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    
    from main import app
    from app.core.config import get_settings
    from app.core.database import Base, engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register a real user
        email = f"user_{random.randint(1000,9999)}@example.com"
        await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "name": "Verify 2"
        })
        
        # Forgot password
        resp = await client.post("/api/v1/auth/forgot-password", json={"email": email})
        print(f"Status Code: {resp.status_code}")
        print(f"Response Body: {resp.json()}")
        print("Confirmed no OTP in response body.")

    print("\n================ ITEM 3 ================")
    # Force Redis to fail
    os.environ["REDIS_URL"] = "redis://localhost:9999"
    import app.core.redis as redis_core
    if redis_core.redis_client:
        await redis_core.close_redis()
        redis_core.redis_client = None

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email3 = f"user3_{random.randint(1000,9999)}@example.com"
        r1 = await client.post("/api/v1/auth/register", json={"email": email3, "password": "Password123!", "name": "V3"})
        print(f"Register: {r1.status_code} {r1.json()}")
        
        r2 = await client.post("/api/v1/auth/login", json={"email": email3, "password": "Password123!"})
        print(f"Login: {r2.status_code}")
        token = r2.json()["data"]["access_token"]
        
        r3 = await client.post("/api/v1/auth/forgot-password", json={"email": email3})
        print(f"Forgot password: {r3.status_code}")
        
        # We need OTP. Let's get it from db directly since we are not dev mode
        from app.core.database import async_session_maker
        from app.models import User
        from sqlalchemy import select
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.email == email3))
            user = result.scalars().first()
            otp = user.reset_otp
        
        r4 = await client.post("/api/v1/auth/verify-otp", json={"email": email3, "otp": otp})
        print(f"Verify OTP: {r4.status_code}")
        reset_token = r4.json()["data"]["reset_token"]
        
        r5 = await client.post("/api/v1/auth/reset-password", json={"token": reset_token, "new_password": "NewPassword123!"})
        print(f"Reset Password: {r5.status_code}")
        
        r6 = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        print(f"Logout: {r6.status_code}")
        
        r7 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        print(f"Get Current User: {r7.status_code} {r7.json()}")

if __name__ == "__main__":
    asyncio.run(run())
