"""
Tests de integracion para el endpoint /health.
"""

import pytest


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health_returns_200(self, client) -> None:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    async def test_health_returns_status(self, client) -> None:
        response = await client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "healthy"

    async def test_health_returns_components(self, client) -> None:
        response = await client.get("/api/v1/health")
        data = response.json()
        assert "components" in data
        assert "database" in data["components"]
        assert "version" in data

    async def test_health_returns_uptime(self, client) -> None:
        response = await client.get("/api/v1/health")
        data = response.json()
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0
