"""
Conexion a PostgreSQL con SQLAlchemy async.

Configura el engine y la session factory para operaciones asincronas.
"""

import ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _build_connect_args() -> dict:
    """
    Construye connect_args para asyncpg.
    DO Managed PostgreSQL requiere SSL pero usa self-signed cert en la cadena,
    por lo que se deshabilita la verificacion del certificado.
    """
    if not settings.db_requires_ssl:
        return {}
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    return {"ssl": ssl_ctx}


engine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.app_debug,
    connect_args=_build_connect_args(),
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy."""

    pass
