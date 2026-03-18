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
    - SSL sin verificacion de cert (DO managed PG usa self-signed chain)
    - search_path apunta al schema 'app' (usuario propio) para evitar el
      restriction de PG 15 sobre CREATE en schema 'public'
    """
    connect_args: dict = {
        "server_settings": {"search_path": "app,public"},
    }
    if settings.db_requires_ssl:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx
    return connect_args


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
