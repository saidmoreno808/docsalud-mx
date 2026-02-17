"""
Tests de integracion para el endpoint de upload.
"""

import io

import pytest


@pytest.mark.asyncio
class TestUploadDocument:
    async def test_upload_rejects_unsupported_type(self, client) -> None:
        files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
        response = await client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert "no soportado" in response.json()["detail"]

    async def test_upload_rejects_large_file(self, client) -> None:
        content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("big.jpg", io.BytesIO(content), "image/jpeg")}
        response = await client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert "grande" in response.json()["detail"]

    async def test_upload_accepts_jpeg(self, client) -> None:
        # Minimal JPEG header
        content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        files = {"file": ("doc.jpg", io.BytesIO(content), "image/jpeg")}
        response = await client.post("/api/v1/upload", files=files)
        # Should be 202 (accepted for processing), even if OCR will fail
        assert response.status_code == 202
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "processing"

    async def test_upload_accepts_pdf(self, client) -> None:
        content = b"%PDF-1.4" + b"\x00" * 100
        files = {"file": ("doc.pdf", io.BytesIO(content), "application/pdf")}
        response = await client.post("/api/v1/upload", files=files)
        assert response.status_code == 202


@pytest.mark.asyncio
class TestProcessingStatus:
    async def test_status_not_found(self, client) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/upload/{fake_id}/status")
        assert response.status_code == 404

    async def test_status_after_upload(self, client) -> None:
        content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        files = {"file": ("doc.jpg", io.BytesIO(content), "image/jpeg")}
        upload_resp = await client.post("/api/v1/upload", files=files)
        doc_id = upload_resp.json()["document_id"]

        response = await client.get(f"/api/v1/upload/{doc_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == doc_id
        assert data["status"] in ("processing", "completed", "failed")
