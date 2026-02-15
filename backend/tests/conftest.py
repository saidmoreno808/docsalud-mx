"""
Fixtures compartidos para tests.

Configura cliente HTTP de prueba, base de datos en memoria,
y datos de prueba reutilizables.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Cliente HTTP async para testing de endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
