"""
Fixtures para tests de integracion de la API.

Usa SQLite async en memoria para evitar dependencia de PostgreSQL.
Registra compiladores para tipos PostgreSQL no soportados en SQLite.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import JSON, Column, String, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

from app.db.database import Base
from app.dependencies import get_db
from app.main import app


# Teach SQLite how to compile JSONB -> JSON
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kwargs):
    return "JSON"


# SQLite async in-memory engine
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Crea y destruye tablas para cada test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(_create_tables)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def _create_tables(connection, **kwargs):
    """Crea tablas adaptando tipos no soportados por SQLite."""
    from app.db.models import DocumentEmbedding

    # Replace pgvector Vector column with nullable String for SQLite
    table = DocumentEmbedding.__table__
    if "embedding" in table.c:
        col = table.c["embedding"]
        if not isinstance(col.type, String):
            table._columns.remove(col)
            table.append_column(Column("embedding", String, nullable=True))

    Base.metadata.create_all(connection)


async def override_get_db():
    """Override de la dependencia get_db para tests."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def client():
    """Cliente HTTP async para tests de integracion."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session():
    """Sesion de DB para tests que necesitan acceso directo."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def sample_patient_data() -> dict:
    """Datos de paciente de prueba."""
    return {
        "first_name": "Juan",
        "last_name": "Perez Lopez",
        "external_id": "PELJ900101HSPRRN01",
        "date_of_birth": "1990-01-01",
        "gender": "M",
        "blood_type": "O+",
        "chronic_conditions": ["diabetes_tipo_2", "hipertension"],
    }
