"""
Pydantic schemas para endpoints de pacientes.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """Schema para crear un paciente."""

    external_id: str | None = Field(None, max_length=50, description="CURP o ID de clinica")
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: date | None = None
    gender: str | None = Field(None, max_length=10)
    blood_type: str | None = Field(None, max_length=5)
    chronic_conditions: list[str] = Field(default_factory=list)


class PatientUpdate(BaseModel):
    """Schema para actualizar un paciente."""

    external_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_type: str | None = None
    chronic_conditions: list[str] | None = None


class PatientResponse(BaseModel):
    """Schema de respuesta de paciente."""

    id: uuid.UUID
    external_id: str | None = None
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    gender: str | None = None
    blood_type: str | None = None
    chronic_conditions: list[str] = Field(default_factory=list)
    risk_score: float = 0.0
    risk_cluster: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    """Respuesta paginada de pacientes."""

    items: list[PatientResponse]
    total: int
    page: int
    pages: int
