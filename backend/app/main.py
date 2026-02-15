"""
DocSalud MX — API Principal.

FastAPI application con middleware, routers, y lifecycle management.
Sistema de Digitalizacion Inteligente de Expedientes Clinicos.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.middleware.cors import setup_cors
from app.api.v1.router import api_router
from app.config import settings
from app.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestion del ciclo de vida de la aplicacion.

    Startup:
        - Configurar logging
        - Inicializar conexion a base de datos
        - Cargar modelos ML en memoria (futuras fases)

    Shutdown:
        - Cerrar pool de conexiones
        - Liberar memoria de modelos
    """
    setup_logging()
    logger.info("starting_application", app_name=settings.app_name, env=settings.app_env)

    yield

    logger.info("shutting_down_application")


app = FastAPI(
    title="DocSalud MX API",
    description="Sistema de Digitalizacion Inteligente de Expedientes Clinicos",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_cors(app)
app.include_router(api_router)
