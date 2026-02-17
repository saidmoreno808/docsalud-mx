"""
Pydantic schemas para endpoints de alertas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    """Schema de respuesta de alerta."""

    id: uuid.UUID
    patient_id: uuid.UUID
    document_id: uuid.UUID | None = None
    alert_type: str
    severity: str
    title: str
    description: str | None = None
    is_resolved: bool = False
    resolved_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertSummary(BaseModel):
    """Resumen de alertas por severidad."""

    total: int
    critical: int
    high: int
    medium: int
    low: int


class AlertListResponse(BaseModel):
    """Respuesta de alertas con resumen."""

    alerts: list[AlertResponse]
    summary: AlertSummary


class AlertResolveRequest(BaseModel):
    """Request para resolver una alerta."""

    resolution_note: str | None = Field(None, max_length=500)
