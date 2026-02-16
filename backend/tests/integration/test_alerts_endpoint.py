"""
Tests de integracion para endpoints de alertas.
"""

import uuid

import pytest

from app.db.models import Alert, Patient


@pytest.mark.asyncio
class TestListAlerts:
    async def test_list_empty(self, client) -> None:
        response = await client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert data["alerts"] == []
        assert data["summary"]["total"] == 0

    async def test_list_with_alerts(self, client, db_session) -> None:
        # Create patient and alert directly in DB
        patient = Patient(
            first_name="Test",
            last_name="Patient",
        )
        db_session.add(patient)
        await db_session.flush()

        alert = Alert(
            patient_id=patient.id,
            alert_type="glucosa_alta",
            severity="high",
            title="Glucosa elevada",
            description="Glucosa en 250 mg/dL",
        )
        db_session.add(alert)
        await db_session.commit()

        response = await client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["severity"] == "high"
        assert data["summary"]["high"] == 1
        assert data["summary"]["total"] == 1

    async def test_list_filter_by_severity(self, client, db_session) -> None:
        patient = Patient(first_name="Test", last_name="Patient")
        db_session.add(patient)
        await db_session.flush()

        for sev in ["low", "medium", "high"]:
            alert = Alert(
                patient_id=patient.id,
                alert_type="test",
                severity=sev,
                title=f"Alert {sev}",
            )
            db_session.add(alert)
        await db_session.commit()

        response = await client.get("/api/v1/alerts?severity=high")
        data = response.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["severity"] == "high"


@pytest.mark.asyncio
class TestResolveAlert:
    async def test_resolve_existing(self, client, db_session) -> None:
        patient = Patient(first_name="Test", last_name="Patient")
        db_session.add(patient)
        await db_session.flush()

        alert = Alert(
            patient_id=patient.id,
            alert_type="test",
            severity="medium",
            title="Test alert",
        )
        db_session.add(alert)
        await db_session.commit()

        response = await client.patch(f"/api/v1/alerts/{alert.id}/resolve")
        assert response.status_code == 200
        data = response.json()
        assert data["is_resolved"] is True

    async def test_resolve_not_found(self, client) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(f"/api/v1/alerts/{fake_id}/resolve")
        assert response.status_code == 404
