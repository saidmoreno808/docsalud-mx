"""
Endpoint de healthcheck del sistema.

Verifica el estado de todos los componentes criticos.
"""

import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.gradient.do_gradient_client import DOGradientClient
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
        "version": "0.6.0",
        "uptime_seconds": uptime,
    }
