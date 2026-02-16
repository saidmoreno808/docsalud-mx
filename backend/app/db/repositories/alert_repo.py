"""
Repositorio de alertas.

Encapsula operaciones de base de datos para la tabla alerts.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Alert


class AlertRepository:
    """Repositorio para operaciones CRUD de alertas."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        patient_id: uuid.UUID,
        alert_type: str,
        severity: str,
        title: str,
        description: str | None = None,
        document_id: uuid.UUID | None = None,
    ) -> Alert:
        """Crea una nueva alerta."""
        alert = Alert(
            patient_id=patient_id,
            document_id=document_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
        )
        self._session.add(alert)
        await self._session.flush()
        return alert

    async def get_by_id(self, alert_id: uuid.UUID) -> Alert | None:
        """Obtiene una alerta por ID."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_alerts(
        self,
        patient_id: uuid.UUID | None = None,
        severity: str | None = None,
        is_resolved: bool = False,
    ) -> list[Alert]:
        """Lista alertas con filtros opcionales."""
        stmt = select(Alert).where(Alert.is_resolved == is_resolved)

        if patient_id:
            stmt = stmt.where(Alert.patient_id == patient_id)
        if severity:
            stmt = stmt.where(Alert.severity == severity)

        stmt = stmt.order_by(Alert.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_summary(
        self, patient_id: uuid.UUID | None = None
    ) -> dict[str, int]:
        """Obtiene resumen de alertas por severidad."""
        stmt = select(Alert.severity, func.count(Alert.id)).where(
            Alert.is_resolved == False  # noqa: E712
        )
        if patient_id:
            stmt = stmt.where(Alert.patient_id == patient_id)
        stmt = stmt.group_by(Alert.severity)

        result = await self._session.execute(stmt)
        counts = dict(result.all())

        return {
            "total": sum(counts.values()),
            "critical": counts.get("critical", 0),
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
        }

    async def resolve(self, alert_id: uuid.UUID) -> Alert | None:
        """Marca una alerta como resuelta."""
        alert = await self.get_by_id(alert_id)
        if alert is None:
            return None
        alert.is_resolved = True
        alert.resolved_at = datetime.now(timezone.utc)
        await self._session.flush()
        return alert
