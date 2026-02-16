"""
Endpoint de upload de documentos.

POST /upload — Recibe imagen o PDF y lanza procesamiento.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.upload import ProcessingStatusResponse, UploadResponse
from app.dependencies import get_db
from app.services.document_service import DocumentService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["upload"])

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/tiff",
    "application/pdf",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_document(
    file: UploadFile,
    patient_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Sube un documento para procesamiento.

    Args:
        file: Archivo (image/jpeg, image/png, image/tiff, application/pdf).
        patient_id: ID del paciente asociado (opcional).

    Returns:
        ID del documento y status de procesamiento.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado: {file.content_type}. "
            f"Permitidos: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Maximo: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    service = DocumentService(db)
    document_id = await service.upload_and_process(
        file_content=content,
        filename=file.filename or "unnamed",
        patient_id=patient_id,
    )

    return UploadResponse(
        document_id=document_id,
        status="processing",
        message="Documento recibido, procesamiento iniciado",
    )


@router.get("/upload/{document_id}/status", response_model=ProcessingStatusResponse)
async def get_processing_status(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProcessingStatusResponse:
    """Consulta el estado de procesamiento de un documento."""
    service = DocumentService(db)
    document = await service.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return ProcessingStatusResponse(
        document_id=document.id,
        status=document.processing_status,
        document_type=document.document_type,
        document_type_confidence=document.document_type_confidence,
        ocr_confidence=document.ocr_confidence,
        processing_time_ms=document.processing_time_ms,
        created_at=document.created_at,
    )
