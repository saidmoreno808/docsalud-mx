"""
Router principal de la API v1.

Agrega todos los sub-routers de endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
