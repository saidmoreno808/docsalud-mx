"""
DocSalud MX — API Principal.

FastAPI application con middleware, routers, y lifecycle management.
Sistema de Digitalizacion Inteligente de Expedientes Clinicos.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.middleware.cors import setup_cors
from app.api.middleware.logging import LoggingMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
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
        - Cargar modelos ML en memoria
        - Verificar conexion a Supabase

    Shutdown:
        - Cerrar pool de conexiones
        - Liberar memoria de modelos
    """
    setup_logging()
    logger.info("starting_application", app_name=settings.app_name, env=settings.app_env)

    # Verify database connection
    try:
        from app.db.database import engine

        async with engine.begin() as conn:
            from sqlalchemy import text

            await conn.execute(text("SELECT 1"))
        logger.info("database_connected")
    except Exception:
        logger.warning("database_connection_failed")

    yield

    # Shutdown
    try:
        from app.db.database import engine

        await engine.dispose()
        logger.info("database_connections_closed")
    except Exception:
        pass

    logger.info("shutting_down_application")


app = FastAPI(
    title="DocSalud MX API",
    description="Sistema de Digitalizacion Inteligente de Expedientes Clinicos",
    version="0.6.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_cors(app)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
app.include_router(api_router)
