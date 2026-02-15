"""
Inyeccion de dependencias para FastAPI.

Centraliza la creacion de dependencias reutilizables
como sesiones de base de datos, servicios, y clientes externos.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesion de base de datos por request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
