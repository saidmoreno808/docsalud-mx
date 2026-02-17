"""
Servicio de busqueda semantica y consultas RAG.

Nota: La funcionalidad completa de RAG (Phase 4) aun no esta implementada.
Este servicio proporciona stubs que retornan respuestas placeholder hasta
que el modulo RAG este listo.
"""

import uuid

from app.api.v1.schemas.query import (
    ClassifyResponse,
    QueryResponse,
    SearchResponse,
    SearchResultItem,
    SourceReference,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SearchService:
    """Servicio de busqueda semantica y consultas en lenguaje natural."""

    async def search(
        self,
        query: str,
        patient_id: uuid.UUID | None = None,
        top_k: int = 5,
    ) -> SearchResponse:
        """
        Busqueda semantica sobre documentos.

        TODO: Implementar con vector store en Fase 4.
        """
        logger.info("search_requested", query=query, patient_id=str(patient_id) if patient_id else None)
        return SearchResponse(results=[])

    async def query(
        self,
        question: str,
        patient_id: uuid.UUID | None = None,
        query_type: str = "general",
    ) -> QueryResponse:
        """
        Consulta en lenguaje natural sobre expedientes.

        TODO: Implementar RAG chain completo en Fase 4.
        """
        logger.info("query_requested", question=question, query_type=query_type)
        return QueryResponse(
            answer="El modulo RAG aun no esta implementado. Disponible en Fase 4.",
            sources=[],
            confidence=0.0,
        )

    def classify_text(self, text: str) -> ClassifyResponse:
        """Clasifica texto de documento usando ML."""
        try:
            from app.core.nlp.classifier import DocumentClassifier

            classifier = DocumentClassifier()
            result = classifier.classify(text)
            return ClassifyResponse(
                document_type=result.document_type,
                confidence=result.confidence,
                all_probabilities=result.all_probabilities,
                model_used="heuristic",
            )
        except Exception:
            logger.warning("classify_fallback")
            return ClassifyResponse(
                document_type="otro",
                confidence=0.0,
                all_probabilities={},
                model_used="fallback",
            )
