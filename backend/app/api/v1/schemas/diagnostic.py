"""
Pydantic schemas para el endpoint de diagnostico predictivo.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DiagnosticResponse(BaseModel):
    """Respuesta del motor de diagnostico predictivo."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    risk_score: float
    risk_level: str
    anomalies: list[str]
    recommendations: list[str]
    referred_to: str | None
    suggested_studies: list[str]
    confidence: float
    sources_used: list[str]
    gradient_model_used: str
    created_at: datetime
