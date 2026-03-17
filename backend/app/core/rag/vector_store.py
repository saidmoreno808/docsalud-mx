"""
Interface con Supabase/pgvector para busqueda semantica.

Stub funcional — se expande en fases posteriores con implementacion
completa de similarity search y hybrid search.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger()


class VectorStore:
    """Almacenamiento y busqueda vectorial con pgvector."""

    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_patient_id: str | None = None,
    ) -> list[dict]:
        """
        Busqueda por similitud coseno.

        Args:
            query: Texto de busqueda.
            k: Numero de resultados a retornar.
            filter_patient_id: Filtrar por patient_id (opcional).

        Returns:
            Lista de resultados con id, chunk_text, score, summary.
        """
        logger.debug("vector_store_similarity_search", query=query[:80], k=k)
        return []

    async def store_embeddings(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        """
        Almacena chunks con sus embeddings en pgvector.

        Args:
            document_id: UUID del documento.
            chunks: Lista de fragmentos de texto.
            embeddings: Lista de vectores de embedding.
        """
        logger.debug(
            "vector_store_store_embeddings",
            document_id=document_id,
            n_chunks=len(chunks),
        )
