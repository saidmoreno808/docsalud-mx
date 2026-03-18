"""
Endpoint de consultas en lenguaje natural (RAG).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.query import QueryRequest, QueryResponse
from app.dependencies import get_db
from app.services.search_service import SearchService

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Consulta en lenguaje natural sobre expedientes clinicos usando RAG."""
    service = SearchService(session=db)
    return await service.query(
        question=request.question,
        patient_id=request.patient_id,
        query_type=request.query_type,
    )
