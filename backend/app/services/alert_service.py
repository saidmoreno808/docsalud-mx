"""
Servicio de logica de negocio para alertas clinicas.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.alert import AlertListResponse, AlertResponse, AlertSummary
from app.db.models import Alert
from app.db.repositories.alert_repo import AlertRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AlertService:
    """Logica de negocio para alertas clinicas."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = AlertRepository(session)

    async def list_alerts(
        self,
        patient_id: uuid.UUID | None = None,
        severity: str | None = None,
        is_resolved: bool = False,
    ) -> AlertListResponse:
        """Lista alertas con resumen."""
        alerts = await self._repo.list_alerts(
            patient_id=patient_id, severity=severity, is_resolved=is_resolved
        )
        summary_data = await self._repo.get_summary(patient_id=patient_id)

        return AlertListResponse(
            alerts=[AlertResponse.model_validate(a) for a in alerts],
            summary=AlertSummary(**summary_data),
        )

    async def resolve_alert(self, alert_id: uuid.UUID) -> Alert | None:
        """Marca una alerta como resuelta."""
        alert = await self._repo.resolve(alert_id)
        if alert:
            logger.info("alert_resolved", alert_id=str(alert_id))
        return alert

    async def create_alert(
        self,
        patient_id: uuid.UUID,
        alert_type: str,
        severity: str,
        title: str,
        description: str | None = None,
        document_id: uuid.UUID | None = None,
    ) -> Alert:
        """Crea una nueva alerta."""
        alert = await self._repo.create(
            patient_id=patient_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            document_id=document_id,
        )
        logger.info(
            "alert_created",
            alert_id=str(alert.id),
            severity=severity,
            patient_id=str(patient_id),
        )
        return alert
