"""
Tests de integracion para endpoints de pacientes.
"""

import pytest


@pytest.mark.asyncio
class TestCreatePatient:
    async def test_create_patient_success(self, client, sample_patient_data) -> None:
        response = await client.post("/api/v1/patients", json=sample_patient_data)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Juan"
        assert data["last_name"] == "Perez Lopez"
        assert "id" in data

    async def test_create_patient_minimal(self, client) -> None:
        response = await client.post(
            "/api/v1/patients",
            json={"first_name": "Maria", "last_name": "Garcia"},
        )
        assert response.status_code == 201

    async def test_create_patient_missing_name(self, client) -> None:
        response = await client.post(
            "/api/v1/patients",
            json={"first_name": "Solo"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestListPatients:
    async def test_list_empty(self, client) -> None:
        response = await client.get("/api/v1/patients")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_with_patients(self, client, sample_patient_data) -> None:
        await client.post("/api/v1/patients", json=sample_patient_data)
        response = await client.get("/api/v1/patients")
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    async def test_list_pagination(self, client) -> None:
        for i in range(3):
            await client.post(
                "/api/v1/patients",
                json={"first_name": f"Paciente{i}", "last_name": "Test"},
            )
        response = await client.get("/api/v1/patients?page=1&page_size=2")
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["pages"] == 2

    async def test_list_search(self, client, sample_patient_data) -> None:
        await client.post("/api/v1/patients", json=sample_patient_data)
        await client.post(
            "/api/v1/patients",
            json={"first_name": "Maria", "last_name": "Lopez"},
        )
        response = await client.get("/api/v1/patients?search=Juan")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["first_name"] == "Juan"


@pytest.mark.asyncio
class TestGetPatient:
    async def test_get_existing(self, client, sample_patient_data) -> None:
        create_resp = await client.post("/api/v1/patients", json=sample_patient_data)
        patient_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/patients/{patient_id}")
        assert response.status_code == 200
        assert response.json()["id"] == patient_id

    async def test_get_not_found(self, client) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/patients/{fake_id}")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdatePatient:
    async def test_update_name(self, client, sample_patient_data) -> None:
        create_resp = await client.post("/api/v1/patients", json=sample_patient_data)
        patient_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/patients/{patient_id}",
            json={"first_name": "Carlos"},
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Carlos"

    async def test_update_not_found(self, client) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/api/v1/patients/{fake_id}",
            json={"first_name": "Test"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeletePatient:
    async def test_delete_existing(self, client, sample_patient_data) -> None:
        create_resp = await client.post("/api/v1/patients", json=sample_patient_data)
        patient_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/patients/{patient_id}")
        assert response.status_code == 204

        get_response = await client.get(f"/api/v1/patients/{patient_id}")
        assert get_response.status_code == 404

    async def test_delete_not_found(self, client) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/patients/{fake_id}")
        assert response.status_code == 404
