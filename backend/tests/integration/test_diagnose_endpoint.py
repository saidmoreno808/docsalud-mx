"""
Tests de integracion para POST /api/v1/diagnose.

DOGradientClient se mockea para no consumir creditos en CI.
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GRADIENT_JSON_RESPONSE = json.dumps({
    "nivel_riesgo": "MODERADO",
    "hallazgos_criticos": ["Glucosa en limite alto"],
    "recomendaciones": ["Control glucémico en 3 meses", "Dieta hipocalórica"],
    "derivacion": None,
    "estudios_sugeridos": ["Hemoglobina glucosilada (HbA1c)"],
    "confianza": 0.82,
})

GRADIENT_CRITICO_RESPONSE = json.dumps({
    "nivel_riesgo": "CRÍTICO",
    "hallazgos_criticos": ["HbA1c 11.5% — descontrol severo", "Glucosa 380 mg/dL"],
    "recomendaciones": ["Ingreso hospitalario urgente", "Ajuste de insulina"],
    "derivacion": "Endocrinología",
    "estudios_sugeridos": ["Panel metabólico completo"],
    "confianza": 0.91,
})


def _mock_gradient_client(response_text: str = GRADIENT_JSON_RESPONSE):
    """Patch DOGradientClient.complete para devolver respuesta fija."""
    mock_instance = MagicMock()
    mock_instance.complete = AsyncMock(return_value=response_text)
    mock_instance.model = "test-llm-mock"
    mock_cls = MagicMock(return_value=mock_instance)
    return mock_cls


# ---------------------------------------------------------------------------
# Tests: happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_diagnose_returns_200(client: AsyncClient, sample_patient_data: dict):
    """Diagnostico completo devuelve 200 con DiagnosticResponse valido."""
    # Create patient
    resp = await client.post("/api/v1/patients/", json=sample_patient_data)
    assert resp.status_code == 201
    patient_id = resp.json()["id"]

    with patch(
        "app.api.v1.endpoints.diagnose.DOGradientClient",
        _mock_gradient_client(),
    ):
        resp = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["patient_id"] == patient_id
    assert data["risk_level"] in {"BAJO", "MODERADO", "ALTO", "CRÍTICO"}
    assert isinstance(data["risk_score"], (int, float))
    assert isinstance(data["recommendations"], list)
    assert isinstance(data["anomalies"], list)
    assert isinstance(data["confidence"], float)
    assert "gradient_model_used" in data
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_diagnose_risk_level_from_gradient(
    client: AsyncClient, sample_patient_data: dict
):
    """El risk_level proviene de la respuesta de DO Gradient AI."""
    resp = await client.post("/api/v1/patients/", json=sample_patient_data)
    patient_id = resp.json()["id"]

    with patch(
        "app.api.v1.endpoints.diagnose.DOGradientClient",
        _mock_gradient_client(GRADIENT_JSON_RESPONSE),
    ):
        resp = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")

    assert resp.status_code == 200
    assert resp.json()["risk_level"] == "MODERADO"


@pytest.mark.asyncio
async def test_diagnose_recommendations_populated(
    client: AsyncClient, sample_patient_data: dict
):
    """Las recomendaciones del LLM se incluyen en la respuesta."""
    resp = await client.post("/api/v1/patients/", json=sample_patient_data)
    patient_id = resp.json()["id"]

    with patch(
        "app.api.v1.endpoints.diagnose.DOGradientClient",
        _mock_gradient_client(),
    ):
        resp = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")

    data = resp.json()
    assert len(data["recommendations"]) > 0
    assert "Control glucémico en 3 meses" in data["recommendations"]


@pytest.mark.asyncio
async def test_diagnose_referred_to_null_when_not_needed(
    client: AsyncClient, sample_patient_data: dict
):
    """referred_to es null cuando el LLM no indica derivacion."""
    resp = await client.post("/api/v1/patients/", json=sample_patient_data)
    patient_id = resp.json()["id"]

    with patch(
        "app.api.v1.endpoints.diagnose.DOGradientClient",
        _mock_gradient_client(GRADIENT_JSON_RESPONSE),
    ):
        resp = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")

    assert resp.json()["referred_to"] is None


@pytest.mark.asyncio
async def test_diagnose_critico_includes_referred_to(
    client: AsyncClient, sample_patient_data: dict
):
    """Diagnostico CRITICO incluye especialidad de derivacion."""
    resp = await client.post("/api/v1/patients/", json=sample_patient_data)
    patient_id = resp.json()["id"]

    with patch(
        "app.api.v1.endpoints.diagnose.DOGradientClient",
        _mock_gradient_client(GRADIENT_CRITICO_RESPONSE),
    ):
        resp = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")

    data = resp.json()
    assert data["risk_level"] == "CRÍTICO"
    assert data["referred_to"] == "Endocrinología"


# ---------------------------------------------------------------------------
# Tests: error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_diagnose_patient_not_found(client: AsyncClient):
    """Retorna 404 si el patient_id no existe."""
    unknown_id = str(uuid.uuid4())
    with patch(
        "app.api.v1.endpoints.diagnose.DOGradientClient",
        _mock_gradient_client(),
    ):
        resp = await client.post(f"/api/v1/diagnose?patient_id={unknown_id}")

    assert resp.status_code == 404
    assert "no encontrado" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_diagnose_invalid_uuid(client: AsyncClient):
    """Retorna 422 si el patient_id no es un UUID valido."""
    resp = await client.post("/api/v1/diagnose?patient_id=not-a-uuid")
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Tests: LLM fallback when gradient returns invalid JSON
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_diagnose_fallback_when_llm_returns_garbage(
    client: AsyncClient, sample_patient_data: dict
):
    """Si el LLM devuelve texto sin JSON, se usan valores fallback."""
    resp = await client.post("/api/v1/patients/", json=sample_patient_data)
    patient_id = resp.json()["id"]

    with patch(
        "app.api.v1.endpoints.diagnose.DOGradientClient",
        _mock_gradient_client("Lo siento, no puedo responder."),
    ):
        resp = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")

    assert resp.status_code == 200
    data = resp.json()
    # risk_level should fallback to ML score-based level
    assert data["risk_level"] in {"BAJO", "MODERADO", "ALTO", "CRÍTICO"}
    assert data["risk_score"] >= 0


# ---------------------------------------------------------------------------
# Tests: result is persisted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_diagnose_result_persisted(
    client: AsyncClient, sample_patient_data: dict
):
    """El resultado se guarda en la DB (segunda llamada genera nuevo registro)."""
    resp = await client.post("/api/v1/patients/", json=sample_patient_data)
    patient_id = resp.json()["id"]

    mock_cls = _mock_gradient_client()
    with patch("app.api.v1.endpoints.diagnose.DOGradientClient", mock_cls):
        r1 = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")
        r2 = await client.post(f"/api/v1/diagnose?patient_id={patient_id}")

    assert r1.status_code == 200
    assert r2.status_code == 200
    # Each call generates a unique ID
    assert r1.json()["id"] != r2.json()["id"]
