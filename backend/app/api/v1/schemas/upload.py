"""
Pydantic schemas para el endpoint de upload de documentos.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Respuesta al subir un documento."""

    document_id: uuid.UUID
    status: str = Field(default="processing", description="Estado del procesamiento")
    message: str = Field(default="Documento recibido, procesamiento iniciado")


class ProcessingStatusResponse(BaseModel):
    """Estado del procesamiento de un documento."""

    document_id: uuid.UUID
    status: str = Field(description="pending, processing, completed, failed")
    document_type: str | None = None
    document_type_confidence: float | None = None
    ocr_confidence: float | None = None
    processing_time_ms: int | None = None
    created_at: datetime | None = None
