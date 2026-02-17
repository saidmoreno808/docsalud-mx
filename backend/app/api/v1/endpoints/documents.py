"""
Endpoints de documentos procesados.
"""

import math
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.document import DocumentListResponse, DocumentResponse
from app.dependencies import get_db
from app.services.document_service import DocumentService

router = APIRouter(prefix="/patients/{patient_id}/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def list_patient_documents(
    patient_id: uuid.UUID,
    doc_type: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """Lista documentos procesados de un paciente."""
    service = DocumentService(db)
    documents, total = await service.get_patient_documents(
        patient_id=patient_id, doc_type=doc_type, page=page, page_size=page_size
    )
    total_pages = max(1, math.ceil(total / page_size))
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        pages=total_pages,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    patient_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Obtiene un documento procesado por ID."""
    service = DocumentService(db)
    document = await service.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if document.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return DocumentResponse.model_validate(document)
