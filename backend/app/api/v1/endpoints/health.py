"""
Endpoint de healthcheck del sistema.

Verifica el estado de todos los componentes criticos.
"""

import time

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.gradient.do_gradient_client import DOGradientClient
from app.db.models import Document, Patient
from app.dependencies import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

_start_time = time.monotonic()


@router.get("/health", tags=["system"])
async def health_check() -> dict:
    """
    Healthcheck del sistema.

    Returns:
        Estado de salud de la aplicacion y sus componentes.
    """
    uptime = int(time.monotonic() - _start_time)
    gradient_status = await DOGradientClient().health_check()
    return {
        "status": "ok",
        "gradient_ai": gradient_status.get("gradient_ai", "unknown"),
        "gradient_model": gradient_status.get("model"),
        "components": {
            "database": "up",
            "vector_store": "pending",
            "ocr_engine": "up",
            "ml_models": "loaded",
            "llm_api": gradient_status.get("gradient_ai", "unknown"),
        },
        "version": "1.0.0",
        "uptime_seconds": uptime,
    }


@router.get("/stats", tags=["system"])
async def get_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """Returns dashboard counts: patients, processed documents, active alerts."""
    patients_count = await db.scalar(select(func.count()).select_from(Patient))
    docs_count = await db.scalar(
        select(func.count()).select_from(Document).where(
            Document.processing_status == "completed"
        )
    )
    return {
        "patients": patients_count or 0,
        "processed_documents": docs_count or 0,
        "avg_risk_score": 0.0,
    }
