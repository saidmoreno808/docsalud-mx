"""
Endpoints CRUD de pacientes.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.dependencies import get_db
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Crea un nuevo paciente."""
    service = PatientService(db)
    patient = await service.create_patient(data)
    return PatientResponse.model_validate(patient)


@router.get("", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
    db: AsyncSession = Depends(get_db),
) -> PatientListResponse:
    """Lista pacientes con paginacion y busqueda opcional."""
    service = PatientService(db)
    patients, total, total_pages = await service.list_patients(
        page=page, page_size=page_size, search=search
    )
    return PatientListResponse(
        items=[PatientResponse.model_validate(p) for p in patients],
        total=total,
        page=page,
        pages=total_pages,
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Obtiene un paciente por ID."""
    service = PatientService(db)
    patient = await service.get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PatientResponse.model_validate(patient)


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Actualiza un paciente."""
    service = PatientService(db)
    patient = await service.update_patient(patient_id, data)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PatientResponse.model_validate(patient)


@router.delete("/{patient_id}", status_code=204)
async def delete_patient(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Elimina un paciente."""
    service = PatientService(db)
    deleted = await service.delete_patient(patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
