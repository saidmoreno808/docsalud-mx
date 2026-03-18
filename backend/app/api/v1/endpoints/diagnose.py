"""
Endpoint POST /api/v1/diagnose — Diagnostico predictivo con DO Gradient AI.

Recibe el UUID de un paciente, extrae su historial de la DB, corre el motor
de diagnostico predictivo y guarda el resultado. Si el nivel es CRITICO,
genera una alerta en segundo plano.
"""

from __future__ import annotations

import uuid
from datetime import date

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.diagnostic import DiagnosticResponse
from app.core.diagnosis.predictive_engine import PredictiveDiagnosticEngine
from app.core.gradient.do_gradient_client import DOGradientClient
from app.core.ml.anomaly_detector import LabAnomalyDetector
from app.core.ml.risk_clusterer import RiskClusterer
from app.core.rag.vector_store import VectorStore
from app.db.database import async_session_factory
from app.db.models import Alert, DiagnosticResult, Document, ExtractedEntity, Patient
from app.db.repositories.patient_repo import PatientRepository
from app.dependencies import get_db

logger = structlog.get_logger()
router = APIRouter()


# ---------------------------------------------------------------------------
# Engine factory — kept at module level so tests can patch DOGradientClient
# ---------------------------------------------------------------------------


def _build_engine() -> PredictiveDiagnosticEngine:
    """Construye el motor de diagnostico con todos sus componentes."""
    return PredictiveDiagnosticEngine(
        gradient_client=DOGradientClient(),
        risk_clusterer=RiskClusterer(),
        anomaly_detector=LabAnomalyDetector(),
        vector_store=VectorStore(),
    )


# ---------------------------------------------------------------------------
# Background task
# ---------------------------------------------------------------------------


async def _create_critical_alert(patient_id: uuid.UUID, description: str) -> None:
    """Crea alerta de severidad HIGH para pacientes con riesgo CRITICO."""
    async with async_session_factory() as session:
        alert = Alert(
            patient_id=patient_id,
            alert_type="riesgo_critico_ia",
            severity="high",
            title="Riesgo CRÍTICO detectado por IA diagnóstica",
            description=description[:500] if description else None,
        )
        session.add(alert)
        await session.commit()
    logger.info("critical_alert_created", patient_id=str(patient_id))


# ---------------------------------------------------------------------------
# Patient data extractor
# ---------------------------------------------------------------------------


async def _build_patient_data(patient: Patient, db: AsyncSession) -> dict:
    """
    Construye el dict patient_data para el motor de diagnostico.

    Extrae: edad, genero, diagnosticos (chronic_conditions + entidades NER),
    medicamentos (entidades NER de recetas), y lab_values (de laboratorios).
    """
    # Age from date_of_birth
    age = 0
    if patient.date_of_birth:
        today = date.today()
        age = (today - patient.date_of_birth).days // 365

    # Recent completed documents
    stmt = (
        select(Document)
        .where(
            Document.patient_id == patient.id,
            Document.processing_status == "completed",
        )
        .order_by(Document.created_at.desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    docs = list(result.scalars().all())
    doc_ids = [d.id for d in docs]

    # Base diagnoses from chronic_conditions
    diagnoses: list[str] = list(patient.chronic_conditions or [])

    # Medications and lab values from extracted_data JSONB
    medications: list[str] = []
    lab_values: dict = {}

    for doc in docs:
        data = doc.extracted_data or {}
        if doc.document_type == "receta":
            for med in data.get("medicamentos", []):
                nombre = med.get("nombre", "")
                if nombre:
                    medications.append(nombre)
        elif doc.document_type == "laboratorio":
            for res in data.get("resultados", []):
                analisis = res.get("analisis", "")
                valor = res.get("valor")
                if analisis and valor is not None:
                    lab_values[analisis] = valor
        else:
            # "otro" / "nota_medica" — extract diagnoses and meds from NER structured data
            for dx in data.get("diagnosticos", []):
                if dx and dx not in diagnoses:
                    diagnoses.append(dx)
            for med in data.get("medicamentos", []):
                nombre = med.get("nombre", med) if isinstance(med, dict) else med
                if nombre and nombre not in medications:
                    medications.append(nombre)
            # lab values stored as flat dict in "valores_laboratorio"
            for k, v in data.get("valores_laboratorio", {}).items():
                if k and v is not None:
                    lab_values[k] = v

    # Fallback: get medications from NER entities
    if not medications and doc_ids:
        stmt_ents = select(ExtractedEntity).where(
            ExtractedEntity.document_id.in_(doc_ids),
            ExtractedEntity.entity_type == "medicamento",
        ).limit(20)
        ent_result = await db.execute(stmt_ents)
        for ent in ent_result.scalars().all():
            medications.append(ent.entity_value)

    last_visit = docs[0].created_at.isoformat() if docs else None

    return {
        "patient_id": str(patient.id),
        "age": age,
        "gender": patient.gender or "desconocido",
        "diagnoses": diagnoses[:10],
        "medications": medications[:10],
        "lab_values": lab_values,
        "last_visit": last_visit,
    }


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/diagnose", response_model=DiagnosticResponse, tags=["diagnosis"])
async def diagnose_patient(
    patient_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> DiagnosticResponse:
    """
    Ejecuta el diagnostico predictivo de un paciente usando DO Gradient AI.

    Args:
        patient_id: UUID del paciente a diagnosticar.
        background_tasks: Tareas en segundo plano de FastAPI.
        db: Sesion de base de datos.

    Returns:
        DiagnosticResponse con risk score, nivel, anomalias y recomendaciones.

    Raises:
        HTTPException 404: Si el paciente no existe.
    """
    # 1. Obtener paciente
    repo = PatientRepository(db)
    patient = await repo.get_by_id(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # 2. Construir patient_data desde la DB
    patient_data = await _build_patient_data(patient, db)

    # 3. Ejecutar motor de diagnostico
    engine = _build_engine()
    result = await engine.diagnose(patient_data)

    # 4. Persistir resultado en diagnostic_results
    db_result = DiagnosticResult(
        patient_id=patient_id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        anomalies=result.anomalies,
        recommendations=result.recommendations,
        referred_to=result.referred_to,
        suggested_studies=result.suggested_studies,
        confidence=result.confidence,
        sources_used=result.sources_used,
        gradient_model_used=result.gradient_model_used,
    )
    db.add(db_result)
    await db.flush()
    await db.refresh(db_result)

    # 5. Alerta de segundo plano si riesgo CRITICO
    if result.risk_level == "CRÍTICO":
        description = "; ".join(result.anomalies[:3]) if result.anomalies else "Riesgo crítico detectado"
        background_tasks.add_task(_create_critical_alert, patient_id, description)
        logger.warning(
            "critical_risk_detected",
            patient_id=str(patient_id),
            risk_score=result.risk_score,
        )

    logger.info(
        "diagnose_completed",
        patient_id=str(patient_id),
        risk_level=result.risk_level,
        risk_score=result.risk_score,
        confidence=result.confidence,
    )
    return DiagnosticResponse.model_validate(db_result)
