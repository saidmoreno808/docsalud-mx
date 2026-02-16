"""
Servicio de logica de negocio para pacientes.
"""

import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.patient import PatientCreate, PatientUpdate
from app.db.models import Patient
from app.db.repositories.patient_repo import PatientRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PatientService:
    """Logica de negocio para operaciones de pacientes."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = PatientRepository(session)

    async def create_patient(self, data: PatientCreate) -> Patient:
        """Crea un nuevo paciente."""
        patient = await self._repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            external_id=data.external_id,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_type=data.blood_type,
            chronic_conditions=data.chronic_conditions,
        )
        logger.info("patient_created", patient_id=str(patient.id))
        return patient

    async def get_patient(self, patient_id: uuid.UUID) -> Patient | None:
        """Obtiene un paciente por ID."""
        return await self._repo.get_by_id(patient_id)

    async def list_patients(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[Patient], int, int]:
        """
        Lista pacientes con paginacion.

        Returns:
            Tupla de (pacientes, total, total_pages).
        """
        patients, total = await self._repo.list_patients(
            page=page, page_size=page_size, search=search
        )
        total_pages = max(1, math.ceil(total / page_size))
        return patients, total, total_pages

    async def update_patient(
        self, patient_id: uuid.UUID, data: PatientUpdate
    ) -> Patient | None:
        """Actualiza un paciente con campos proporcionados."""
        update_fields = data.model_dump(exclude_unset=True)
        if not update_fields:
            return await self._repo.get_by_id(patient_id)
        patient = await self._repo.update(patient_id, **update_fields)
        if patient:
            logger.info("patient_updated", patient_id=str(patient_id))
        return patient

    async def delete_patient(self, patient_id: uuid.UUID) -> bool:
        """Elimina un paciente."""
        deleted = await self._repo.delete(patient_id)
        if deleted:
            logger.info("patient_deleted", patient_id=str(patient_id))
        return deleted
