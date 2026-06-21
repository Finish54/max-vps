"""Basic smoke tests for FastAPI app."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root():
    """Root endpoint returns service info."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "MAX VPS"
    assert "version" in data
    assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_health():
    """Health endpoint returns OK."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_docs_available():
    """Swagger UI available at /docs."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()


@pytest.mark.asyncio
async def test_openapi_schema():
    """OpenAPI schema available."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "MAX VPS API"
    assert "paths" in schema
    assert "/health" in schema["paths"]


@pytest.mark.asyncio
async def test_cors_preflight():
    """CORS preflight works for allowed origin."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "https://maxvps.online",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
