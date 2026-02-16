"""
Tests de integracion para endpoints de search, query y classify.
"""

import pytest


@pytest.mark.asyncio
class TestSearchEndpoint:
    async def test_search_returns_results(self, client) -> None:
        response = await client.get("/api/v1/search?q=glucosa")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # RAG not implemented yet, so results should be empty
        assert data["results"] == []

    async def test_search_requires_query(self, client) -> None:
        response = await client.get("/api/v1/search")
        assert response.status_code == 422

    async def test_search_short_query_rejected(self, client) -> None:
        response = await client.get("/api/v1/search?q=a")
        assert response.status_code == 422


@pytest.mark.asyncio
class TestQueryEndpoint:
    async def test_query_returns_response(self, client) -> None:
        response = await client.post(
            "/api/v1/query",
            json={"question": "Cuales son los resultados de glucosa?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "confidence" in data
        assert "sources" in data

    async def test_query_with_type(self, client) -> None:
        response = await client.post(
            "/api/v1/query",
            json={
                "question": "Medicamentos del paciente",
                "query_type": "medicamentos",
            },
        )
        assert response.status_code == 200

    async def test_query_invalid_type(self, client) -> None:
        response = await client.post(
            "/api/v1/query",
            json={"question": "test query", "query_type": "invalid_type"},
        )
        assert response.status_code == 422

    async def test_query_too_short(self, client) -> None:
        response = await client.post(
            "/api/v1/query",
            json={"question": "ab"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestClassifyEndpoint:
    async def test_classify_receta(self, client) -> None:
        response = await client.post(
            "/api/v1/classify",
            json={
                "text": "Rx: Metformina 850mg tabletas cada 12 horas por 30 dias. Dx: Diabetes Mellitus tipo 2"
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "document_type" in data
        assert "confidence" in data
        assert "all_probabilities" in data
        assert "model_used" in data

    async def test_classify_too_short(self, client) -> None:
        response = await client.post(
            "/api/v1/classify",
            json={"text": "short"},
        )
        assert response.status_code == 422
