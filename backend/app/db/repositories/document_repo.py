"""
Repositorio de documentos.

Encapsula operaciones de base de datos para la tabla documents y extracted_entities.
"""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Document, ExtractedEntity


class DocumentRepository:
    """Repositorio para operaciones CRUD de documentos."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        document_type: str,
        patient_id: uuid.UUID | None = None,
        original_filename: str | None = None,
        storage_path: str | None = None,
        processing_status: str = "pending",
    ) -> Document:
        """Crea un nuevo registro de documento."""
        document = Document(
            patient_id=patient_id,
            document_type=document_type,
            original_filename=original_filename,
            storage_path=storage_path,
            processing_status=processing_status,
        )
        self._session.add(document)
        await self._session.flush()
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """Obtiene un documento por ID con sus entidades."""
        stmt = (
            select(Document)
            .options(selectinload(Document.entities))
            .where(Document.id == document_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_patient(
        self,
        patient_id: uuid.UUID,
        doc_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Document], int]:
        """Lista documentos de un paciente con filtros y paginacion."""
        stmt = (
            select(Document)
            .options(selectinload(Document.entities))
            .where(Document.patient_id == patient_id)
        )

        if doc_type:
            stmt = stmt.where(Document.document_type == doc_type)
        if date_from:
            stmt = stmt.where(Document.created_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            stmt = stmt.where(Document.created_at <= datetime.combine(date_to, datetime.max.time()))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Document.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        documents = list(result.scalars().all())

        return documents, total

    async def update_processing_result(
        self,
        document_id: uuid.UUID,
        raw_text: str | None = None,
        ocr_confidence: float | None = None,
        document_type: str | None = None,
        document_type_confidence: float | None = None,
        extracted_data: dict[str, Any] | None = None,
        processing_status: str = "completed",
        processing_time_ms: int | None = None,
    ) -> Document | None:
        """Actualiza un documento con resultados del procesamiento."""
        document = await self.get_by_id(document_id)
        if document is None:
            return None

        if raw_text is not None:
            document.raw_text = raw_text
        if ocr_confidence is not None:
            document.ocr_confidence = ocr_confidence
        if document_type is not None:
            document.document_type = document_type
        if document_type_confidence is not None:
            document.document_type_confidence = document_type_confidence
        if extracted_data is not None:
            document.extracted_data = extracted_data
        if processing_time_ms is not None:
            document.processing_time_ms = processing_time_ms
        document.processing_status = processing_status

        await self._session.flush()
        return document

    async def add_entities(
        self, document_id: uuid.UUID, entities: list[dict[str, Any]]
    ) -> list[ExtractedEntity]:
        """Agrega entidades extraidas a un documento."""
        db_entities = []
        for entity_data in entities:
            entity = ExtractedEntity(
                document_id=document_id,
                entity_type=entity_data["entity_type"],
                entity_value=entity_data["entity_value"],
                normalized_value=entity_data.get("normalized_value"),
                confidence=entity_data.get("confidence"),
                start_char=entity_data.get("start_char"),
                end_char=entity_data.get("end_char"),
                metadata_=entity_data.get("metadata", {}),
            )
            self._session.add(entity)
            db_entities.append(entity)

        await self._session.flush()
        return db_entities

    async def delete(self, document_id: uuid.UUID) -> bool:
        """Elimina un documento por ID."""
        document = await self.get_by_id(document_id)
        if document is None:
            return False
        await self._session.delete(document)
        await self._session.flush()
        return True
