"""
Endpoints de alertas clinicas.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.alert import AlertListResponse, AlertResolveRequest, AlertResponse
from app.dependencies import get_db
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    patient_id: uuid.UUID | None = Query(default=None),
    severity: str | None = Query(default=None, pattern="^(low|medium|high|critical)$"),
    is_resolved: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
) -> AlertListResponse:
    """Lista alertas activas con resumen por severidad."""
    service = AlertService(db)
    return await service.list_alerts(
        patient_id=patient_id, severity=severity, is_resolved=is_resolved
    )


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: uuid.UUID,
    body: AlertResolveRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Marca una alerta como resuelta."""
    service = AlertService(db)
    alert = await service.resolve_alert(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return AlertResponse.model_validate(alert)
