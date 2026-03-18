"""
Servicio de busqueda semantica y consultas RAG.

Usa RAGChain + DOGradientClient para responder preguntas en lenguaje natural
sobre los documentos almacenados.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.query import (
    ClassifyResponse,
    QueryResponse,
    SearchResponse,
    SourceReference,
)
from app.core.rag.rag_chain import RAGChain, SearchResult
from app.db.models import Document
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Max characters of raw_text to send as context per document chunk
_CHUNK_MAX_CHARS = 4000


class SearchService:
    """Servicio de busqueda semantica y consultas en lenguaje natural."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def search(
        self,
        query: str,
        patient_id: uuid.UUID | None = None,
        top_k: int = 5,
    ) -> SearchResponse:
        """Busqueda semantica sobre documentos."""
        logger.info("search_requested", query=query)
        return SearchResponse(results=[])

    async def query(
        self,
        question: str,
        patient_id: uuid.UUID | None = None,
        query_type: str = "general",
    ) -> QueryResponse:
        """
        Consulta en lenguaje natural sobre expedientes usando RAG.
        Recupera documentos de la DB y los pasa como contexto al LLM.
        """
        logger.info("query_requested", question=question, query_type=query_type)

        context_chunks: list[SearchResult] = []

        if self._session is not None:
            try:
                context_chunks = await self._fetch_context_chunks(patient_id)
            except Exception:
                logger.warning("context_fetch_failed")

        try:
            rag = RAGChain()
            rag_response = await rag.query(
                question=question,
                context_chunks=context_chunks,
                patient_id=str(patient_id) if patient_id else None,
            )

            sources = [
                SourceReference(
                    document_id=c.document_id,
                    document_type=c.document_type,
                    excerpt=c.chunk_text[:200],
                    relevance_score=c.similarity_score,
                )
                for c in rag_response.sources
            ]

            return QueryResponse(
                answer=rag_response.answer,
                sources=sources,
                confidence=rag_response.confidence,
            )
        except Exception:
            logger.exception("rag_query_failed")
            return QueryResponse(
                answer="An error occurred while processing your query. Please try again.",
                sources=[],
                confidence=0.0,
            )

    async def _fetch_context_chunks(
        self, patient_id: uuid.UUID | None
    ) -> list[SearchResult]:
        """Fetches completed documents from DB and converts them to RAG context chunks."""
        stmt = select(Document).where(
            Document.processing_status == "completed",
            Document.raw_text.isnot(None),
        )
        if patient_id is not None:
            stmt = stmt.where(Document.patient_id == patient_id)

        stmt = stmt.order_by(Document.created_at.desc()).limit(10)
        result = await self._session.execute(stmt)  # type: ignore[union-attr]
        documents = list(result.scalars().all())

        chunks: list[SearchResult] = []
        for doc in documents:
            text = (doc.raw_text or "").strip()
            if not text:
                continue
            chunks.append(
                SearchResult(
                    document_id=str(doc.id),
                    chunk_text=text[:_CHUNK_MAX_CHARS],
                    similarity_score=1.0,
                    document_type=doc.document_type or "document",
                    date=str(doc.created_at.date()) if doc.created_at else "",
                )
            )

        return chunks

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
