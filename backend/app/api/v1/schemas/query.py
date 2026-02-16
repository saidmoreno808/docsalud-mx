"""
Pydantic schemas para endpoints de consultas RAG, busqueda y clasificacion.
"""

import uuid

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request para consulta en lenguaje natural."""

    question: str = Field(..., min_length=3, max_length=1000)
    patient_id: uuid.UUID | None = None
    query_type: str = Field(
        default="general", pattern="^(general|medicamentos|laboratorio|alertas)$"
    )


class SourceReference(BaseModel):
    """Referencia a documento fuente de la respuesta."""

    document_id: uuid.UUID
    document_type: str
    date: str | None = None
    relevance: float


class QueryResponse(BaseModel):
    """Respuesta a consulta en lenguaje natural."""

    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    confidence: float


class ClassifyRequest(BaseModel):
    """Request para clasificar texto de documento."""

    text: str = Field(..., min_length=10, max_length=50000)


class ClassifyResponse(BaseModel):
    """Respuesta de clasificacion de documento."""

    document_type: str
    confidence: float
    all_probabilities: dict[str, float]
    model_used: str


class SearchRequest(BaseModel):
    """Request para busqueda semantica."""

    q: str = Field(..., min_length=2, max_length=500)
    patient_id: uuid.UUID | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResultItem(BaseModel):
    """Resultado individual de busqueda."""

    document_id: uuid.UUID
    chunk_text: str
    similarity_score: float
    document_type: str
    patient_name: str | None = None
    date: str | None = None


class SearchResponse(BaseModel):
    """Respuesta de busqueda semantica."""

    results: list[SearchResultItem] = Field(default_factory=list)
