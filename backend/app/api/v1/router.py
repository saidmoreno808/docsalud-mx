"""
Router principal de la API v1.

Agrega todos los sub-routers de endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    alerts,
    classify,
    documents,
    health,
    patients,
    query,
    search,
    upload,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(patients.router)
api_router.include_router(documents.router)
api_router.include_router(alerts.router)
api_router.include_router(search.router)
api_router.include_router(query.router)
api_router.include_router(classify.router)
