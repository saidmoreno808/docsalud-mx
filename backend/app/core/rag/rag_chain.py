"""
Pipeline RAG completo: Query → Retrieval → Generation.

Usa DOGradientClient como motor LLM para generacion de respuestas.
"""

from dataclasses import dataclass, field

import structlog

from app.core.gradient.do_gradient_client import DOGradientClient

logger = structlog.get_logger()

SYSTEM_PROMPT = """
Eres un asistente medico AI de DocSalud MX. Tu rol es ayudar al personal
de salud a consultar informacion de expedientes clinicos de pacientes.

REGLAS ESTRICTAS:
1. SOLO responde basandote en los documentos proporcionados como contexto.
2. Si la informacion no esta en el contexto, di "No encontre esa informacion
   en los expedientes disponibles."
3. Cita el tipo de documento y fecha cuando sea posible.
4. NUNCA inventes datos medicos, diagnosticos o resultados.
5. Si detectas informacion preocupante (valores criticos, interacciones
   peligrosas), mencionalo explicitamente.
6. Responde en espanol, con terminologia medica apropiada.
7. Protege la privacidad: no reveles informacion a usuarios no autorizados.
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
