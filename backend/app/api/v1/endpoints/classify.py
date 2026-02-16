"""
Endpoint de clasificacion de documentos.
"""

from fastapi import APIRouter

from app.api.v1.schemas.query import ClassifyRequest, ClassifyResponse
from app.services.search_service import SearchService

router = APIRouter(tags=["classify"])


@router.post("/classify", response_model=ClassifyResponse)
async def classify_document(request: ClassifyRequest) -> ClassifyResponse:
    """Clasifica el tipo de un texto de documento medico."""
    service = SearchService()
    return service.classify_text(request.text)
