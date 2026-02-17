"""
Repositorio de pacientes.

Encapsula operaciones de base de datos para la tabla patients.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Patient


class PatientRepository:
    """Repositorio para operaciones CRUD de pacientes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        first_name: str,
        last_name: str,
        external_id: str | None = None,
        date_of_birth: date | None = None,
        gender: str | None = None,
        blood_type: str | None = None,
        chronic_conditions: list[str] | None = None,
    ) -> Patient:
        """Crea un nuevo paciente."""
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            external_id=external_id,
            date_of_birth=date_of_birth,
            gender=gender,
            blood_type=blood_type,
            chronic_conditions=chronic_conditions or [],
        )
        self._session.add(patient)
        await self._session.flush()
        return patient

    async def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        """Obtiene un paciente por ID."""
        stmt = select(Patient).where(Patient.id == patient_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Patient | None:
        """Obtiene un paciente por external_id (CURP)."""
        stmt = select(Patient).where(Patient.external_id == external_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_patients(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[Patient], int]:
        """
        Lista pacientes con paginacion y busqueda opcional.

        Returns:
            Tupla de (lista de pacientes, total de registros).
        """
        stmt = select(Patient)

        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(
                (Patient.first_name.ilike(search_filter))
                | (Patient.last_name.ilike(search_filter))
                | (Patient.external_id.ilike(search_filter))
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Patient.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        patients = list(result.scalars().all())

        return patients, total

    async def update(self, patient_id: uuid.UUID, **kwargs: object) -> Patient | None:
        """Actualiza campos de un paciente."""
        patient = await self.get_by_id(patient_id)
        if patient is None:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(patient, key):
                setattr(patient, key, value)

        patient.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.refresh(patient)
        return patient

    async def delete(self, patient_id: uuid.UUID) -> bool:
        """Elimina un paciente por ID."""
        patient = await self.get_by_id(patient_id)
        if patient is None:
            return False
        await self._session.delete(patient)
        await self._session.flush()
        return True
