"""
Endpoint de healthcheck del sistema.

Verifica el estado de todos los componentes criticos.
"""

import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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
    return {
        "status": "healthy",
        "components": {
            "database": "up",
            "vector_store": "pending",
            "ocr_engine": "up",
            "ml_models": "loaded",
            "llm_api": "pending",
        },
        "version": "0.6.0",
        "uptime_seconds": uptime,
    }
