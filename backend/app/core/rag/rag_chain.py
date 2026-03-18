"""
Pipeline RAG completo: Query → Retrieval → Generation.

Usa DOGradientClient como motor LLM para generacion de respuestas.
"""

from dataclasses import dataclass, field

import structlog

from app.core.gradient.do_gradient_client import DOGradientClient

logger = structlog.get_logger()

SYSTEM_PROMPT = """
You are ClinicaIA, an AI-powered clinical assistant. Your role is to help
healthcare staff query information from patient medical records.

STRICT RULES:
1. ONLY answer based on the documents provided as context.
2. If the information is not in the context, say "I could not find that
   information in the available records."
3. Cite the document type and date whenever possible.
4. NEVER invent medical data, diagnoses, or results.
5. If you detect concerning information (critical values, dangerous
   interactions), mention it explicitly.
6. Respond in English with appropriate medical terminology.
7. Protect privacy: do not reveal information to unauthorized users.
"""


@dataclass
class SearchResult:
    """Fragmento de documento recuperado del vector store."""

    document_id: str
    chunk_text: str
    similarity_score: float
    document_type: str = ""
    date: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class RAGResponse:
    """Respuesta generada por el pipeline RAG."""

    answer: str
    sources: list[SearchResult]
    confidence: float


class RAGChain:
    """Cadena RAG para consultas sobre expedientes clinicos."""

    def __init__(self, gradient_client: DOGradientClient | None = None) -> None:
        self._client = gradient_client or DOGradientClient()

    async def query(
        self,
        question: str,
        context_chunks: list[SearchResult] | None = None,
        patient_id: str | None = None,
    ) -> RAGResponse:
        """
        Ejecuta el pipeline RAG completo.

        Args:
            question: Pregunta del usuario en lenguaje natural.
            context_chunks: Fragmentos de documentos relevantes ya recuperados.
            patient_id: ID del paciente para filtrar busqueda (opcional).

        Returns:
            RAGResponse con respuesta del LLM y fuentes citadas.
        """
        chunks = context_chunks or []
        prompt = self._build_prompt(question, chunks)
        answer = await self._client.complete(
            messages=[{"role": "user", "content": prompt}],
            system=SYSTEM_PROMPT,
            max_tokens=1500,
        )
        confidence = self._estimate_confidence(chunks)
        logger.info(
            "rag_query_completed",
            question_len=len(question),
            chunks_used=len(chunks),
            confidence=confidence,
        )
        return RAGResponse(answer=answer, sources=chunks, confidence=confidence)

    def _build_prompt(self, question: str, context_chunks: list[SearchResult]) -> str:
        """Construye el prompt con el contexto recuperado."""
        if not context_chunks:
            return question

        context_text = "\n\n".join(
            f"[{c.document_type} — {c.date}]\n{c.chunk_text}" for c in context_chunks
        )
        return (
            f"CONTEXTO DE EXPEDIENTES:\n{context_text}\n\nPREGUNTA: {question}"
        )

    def _estimate_confidence(self, chunks: list[SearchResult]) -> float:
        """Calcula confianza promedio basada en similaridad de los chunks."""
        if not chunks:
            return 0.5
        return round(sum(c.similarity_score for c in chunks) / len(chunks), 3)
