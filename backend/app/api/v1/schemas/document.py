"""
Pydantic schemas para endpoints de documentos.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EntityResponse(BaseModel):
    """Entidad extraida de un documento."""

    id: uuid.UUID
    entity_type: str
    entity_value: str
    normalized_value: str | None = None
    confidence: float | None = None
    start_char: int | None = None
    end_char: int | None = None

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    """Schema de respuesta de documento procesado."""

    id: uuid.UUID
    patient_id: uuid.UUID | None = None
    document_type: str
    document_type_confidence: float | None = None
    original_filename: str | None = None
    raw_text: str | None = None
    ocr_confidence: float | None = None
    extracted_data: dict[str, Any] | None = None
    processing_status: str
    processing_time_ms: int | None = None
    created_at: datetime
    entities: list[EntityResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Respuesta paginada de documentos."""

    items: list[DocumentResponse]
    total: int
    page: int
    pages: int
