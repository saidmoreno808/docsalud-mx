"""
Endpoint de busqueda semantica.
"""

import uuid

from fastapi import APIRouter, Query

from app.api.v1.schemas.query import SearchResponse
from app.services.search_service import SearchService

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=2, max_length=500),
    patient_id: uuid.UUID | None = Query(default=None),
    top_k: int = Query(default=5, ge=1, le=20),
) -> SearchResponse:
    """Busqueda semantica sobre documentos."""
    service = SearchService()
    return await service.search(query=q, patient_id=patient_id, top_k=top_k)
