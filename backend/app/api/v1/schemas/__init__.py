"""
Pydantic schemas para la API v1 de DocSalud MX.
"""

from app.api.v1.schemas.alert import (
    AlertListResponse,
    AlertResolveRequest,
    AlertResponse,
    AlertSummary,
)
from app.api.v1.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    EntityResponse,
)
from app.api.v1.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.api.v1.schemas.query import (
    ClassifyRequest,
    ClassifyResponse,
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    SourceReference,
)
from app.api.v1.schemas.upload import ProcessingStatusResponse, UploadResponse

__all__ = [
    "AlertListResponse",
    "AlertResolveRequest",
    "AlertResponse",
    "AlertSummary",
    "ClassifyRequest",
    "ClassifyResponse",
    "DocumentListResponse",
    "DocumentResponse",
    "EntityResponse",
    "PatientCreate",
    "PatientListResponse",
    "PatientResponse",
    "PatientUpdate",
    "ProcessingStatusResponse",
    "QueryRequest",
    "QueryResponse",
    "SearchRequest",
    "SearchResponse",
    "SearchResultItem",
    "SourceReference",
    "UploadResponse",
]
