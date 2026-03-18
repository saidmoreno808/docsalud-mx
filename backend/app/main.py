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

    # Connect to DB
    try:
        from app.db.database import Base, engine
        from app.db import models  # noqa: F401 — ensure all models are registered
        from sqlalchemy import text

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("database_connected")
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))

    # Diagnose DB user + permissions
    try:
        from app.db.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            r = await conn.execute(text(
                "SELECT current_user, "
                "has_schema_privilege(current_user, 'public', 'CREATE') AS pub_create, "
                "has_database_privilege(current_user, current_database(), 'CREATE') AS db_create"
            ))
            row = r.fetchone()
            logger.info("db_diagnostics", user=row[0], pub_create=row[1], db_create=row[2])
    except Exception as diag_err:
        logger.warning("db_diagnostics_failed", error=str(diag_err))

    # Transaction 1: create 'app' schema owned by current user
    # (avoids PG 15 restriction on CREATE in public schema)
    try:
        from app.db.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        logger.info("app_schema_ready")
    except Exception as schema_err:
        logger.warning("app_schema_create_skipped", error=str(schema_err))

    # Transaction 2: create all tables inside 'app' schema (via search_path)
    try:
        from app.db.database import Base, engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_ready")
    except Exception as e:
        logger.error("database_create_tables_failed", error=str(e))

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
