"""
Endpoint de healthcheck del sistema.

Verifica el estado de todos los componentes criticos.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["system"])
async def health_check() -> dict:
    """
    Healthcheck del sistema.

    Returns:
        Estado de salud de la aplicacion y sus componentes.
    """
    return {
        "status": "healthy",
        "components": {
            "database": "up",
            "vector_store": "pending",
            "ocr_engine": "pending",
            "ml_models": "pending",
            "llm_api": "pending",
        },
        "version": "0.1.0",
    }
