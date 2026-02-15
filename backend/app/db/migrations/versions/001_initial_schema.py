"""Initial schema with patients, documents, entities, alerts, embeddings.

Revision ID: 001_initial
Revises: None
Create Date: 2026-02-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # -- patients --
    op.create_table(
        "patients",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("external_id", sa.String(50), unique=True, nullable=True, comment="CURP o ID de clinica"),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("blood_type", sa.String(5), nullable=True),
        sa.Column("chronic_conditions", postgresql.JSONB, server_default="'[]'"),
        sa.Column("risk_score", sa.Float, server_default="0.0"),
        sa.Column("risk_cluster", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # -- documents --
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=True),
        sa.Column("document_type", sa.String(50), nullable=False, comment="receta, laboratorio, nota_medica, referencia"),
        sa.Column("document_type_confidence", sa.Float, nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("storage_path", sa.String(500), nullable=True),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("ocr_confidence", sa.Float, nullable=True),
        sa.Column("extracted_data", postgresql.JSONB, nullable=True),
        sa.Column("processing_status", sa.String(20), server_default="'pending'", comment="pending, processing, completed, failed"),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_documents_patient", "documents", ["patient_id"])
    op.create_index("idx_documents_type", "documents", ["document_type"])

    # -- extracted_entities --
    op.create_table(
        "extracted_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False, comment="medicamento, diagnostico, dosis, fecha, signo_vital"),
        sa.Column("entity_value", sa.Text, nullable=False),
        sa.Column("normalized_value", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("start_char", sa.Integer, nullable=True),
        sa.Column("end_char", sa.Integer, nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="'{}'"),
    )
    op.create_index("idx_entities_document", "extracted_entities", ["document_id"])
    op.create_index("idx_entities_type", "extracted_entities", ["entity_type"])

    # -- alerts --
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("alert_type", sa.String(50), nullable=False, comment="glucosa_alta, sin_seguimiento, interaccion_medicamentos"),
        sa.Column("severity", sa.String(10), nullable=False, comment="low, medium, high, critical"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_resolved", sa.Boolean, server_default="false"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_alerts_patient", "alerts", ["patient_id"])
    op.create_index("idx_alerts_severity", "alerts", ["severity"])
    op.create_index(
        "idx_alerts_unresolved",
        "alerts",
        ["is_resolved"],
        postgresql_where=sa.text("is_resolved = FALSE"),
    )

    # -- document_embeddings (pgvector) --
    op.create_table(
        "document_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="'{}'"),
    )
    op.execute(
        "CREATE INDEX idx_embeddings_vector ON document_embeddings "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.drop_table("document_embeddings")
    op.drop_table("alerts")
    op.drop_table("extracted_entities")
    op.drop_table("documents")
    op.drop_table("patients")
    op.execute("DROP EXTENSION IF EXISTS vector")
