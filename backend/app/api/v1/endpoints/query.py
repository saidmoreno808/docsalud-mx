"""
Endpoint de consultas en lenguaje natural (RAG).
"""

from fastapi import APIRouter

from app.api.v1.schemas.query import QueryRequest, QueryResponse
from app.services.search_service import SearchService

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest) -> QueryResponse:
    """Consulta en lenguaje natural sobre expedientes clinicos."""
    service = SearchService()
    return await service.query(
        question=request.question,
        patient_id=request.patient_id,
        query_type=request.query_type,
    )
