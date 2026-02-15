"""
Modelos SQLAlchemy ORM para DocSalud MX.

Define las tablas: patients, documents, extracted_entities, alerts,
document_embeddings.
"""

import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Patient(Base):
    """Modelo de paciente."""

    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, comment="CURP o ID de clinica"
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    blood_type: Mapped[str | None] = mapped_column(String(5), nullable=True)
    chronic_conditions: Mapped[dict] = mapped_column(JSONB, default=list)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_cluster: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )


class Document(Base):
    """Modelo de documento procesado."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=True
    )
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="receta, laboratorio, nota_medica, referencia",
    )
    document_type_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extracted_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processing_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="pending, processing, completed, failed",
    )
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    patient: Mapped["Patient | None"] = relationship(back_populates="documents")
    entities: Mapped[list["ExtractedEntity"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="document")
    embeddings: Mapped[list["DocumentEmbedding"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_documents_patient", "patient_id"),
        Index("idx_documents_type", "document_type"),
    )


class ExtractedEntity(Base):
    """Modelo de entidad extraida por NER."""

    __tablename__ = "extracted_entities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE")
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="medicamento, diagnostico, dosis, fecha, signo_vital",
    )
    entity_value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_char: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_char: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    document: Mapped["Document"] = relationship(back_populates="entities")

    __table_args__ = (
        Index("idx_entities_document", "document_id"),
        Index("idx_entities_type", "entity_type"),
    )


class Alert(Base):
    """Modelo de alerta clinica."""

    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE")
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True
    )
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="glucosa_alta, sin_seguimiento, interaccion_medicamentos",
    )
    severity: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="low, medium, high, critical"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="alerts")
    document: Mapped["Document | None"] = relationship(back_populates="alerts")

    __table_args__ = (
        Index("idx_alerts_patient", "patient_id"),
        Index("idx_alerts_severity", "severity"),
        Index(
            "idx_alerts_unresolved",
            "is_resolved",
            postgresql_where=sa.text("is_resolved = FALSE"),
        ),
    )


class DocumentEmbedding(Base):
    """Modelo de embedding vectorial para busqueda semantica."""

    __tablename__ = "document_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE")
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(1536), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    document: Mapped["Document"] = relationship(back_populates="embeddings")
