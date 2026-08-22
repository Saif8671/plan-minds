import pytest
from fastapi import FastAPI, Request
from httpx import AsyncClient
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/test-route")
@limiter.limit("2/minute")
async def dummy_route(request: Request):
    return {"status": "ok"}


@pytest.mark.asyncio
async def test_rate_limiter_redis():
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Request 1 - Should succeed
        r1 = await ac.get("/test-route")
        assert r1.status_code == 200

        # Request 2 - Should succeed
        r2 = await ac.get("/test-route")
        assert r2.status_code == 200

        # Request 3 - Should fail with 429 Too Many Requests
        r3 = await ac.get("/test-route")
        assert r3.status_code == 429, f"Expected 429, got {r3.status_code}"

        print("SUCCESS! Rate limiter blocked the third request.")
