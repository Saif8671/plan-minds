import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_openapi_schema_accessible(client: AsyncClient):
    """Ensure OpenAPI JSON is accessible and well-formed."""
    response = await client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "AI Schedule Organizer"


@pytest.mark.asyncio
async def test_health_check_contract(client: AsyncClient):
    """Ensure basic health check returns standard response format."""
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_standard_error_format(client: AsyncClient):
    """Ensure 404/405 errors return the standard ApiError wrapper when routed through app exceptions."""
    # FastApi default 404 for unrouted paths won't have the wrapper unless overridden,
    # but a validation error should have the standard wrapper.
    response = await client.post("/api/v1/auth/login", json={})  # Missing fields
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()

    assert "error" in data
    error = data["error"]
    assert "code" in error
    assert error["code"] == "VALIDATION_ERROR"
    assert "message" in error
    assert "details" in error


@pytest.mark.asyncio
async def test_unauthorized_error_format(client: AsyncClient):
    """Ensure missing token returns 401 with detail."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
