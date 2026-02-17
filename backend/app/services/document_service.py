"""
Servicio de procesamiento de documentos.

Orquesta el pipeline completo: OCR -> NLP -> ML -> Storage.
"""

import time
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.document_repo import DocumentRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)

UPLOAD_DIR = Path("uploads")


class DocumentService:
    """Orquesta OCR, NLP, ML y almacenamiento para cada documento."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._doc_repo = DocumentRepository(session)

    async def upload_and_process(
        self,
        file_content: bytes,
        filename: str,
        patient_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        """
        Recibe un archivo, lo guarda y lanza el procesamiento.

        Args:
            file_content: Contenido binario del archivo.
            filename: Nombre original del archivo.
            patient_id: ID del paciente asociado (opcional).

        Returns:
            ID del documento creado.
        """
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        doc_id = uuid.uuid4()
        ext = Path(filename).suffix.lower()
        storage_path = str(UPLOAD_DIR / f"{doc_id}{ext}")

        Path(storage_path).write_bytes(file_content)

        document = await self._doc_repo.create(
            document_type="pending",
            patient_id=patient_id,
            original_filename=filename,
            storage_path=storage_path,
            processing_status="processing",
        )

        try:
            await self._process_document(document.id, storage_path, ext)
        except Exception:
            logger.exception("document_processing_failed", document_id=str(document.id))
            await self._doc_repo.update_processing_result(
                document.id, processing_status="failed"
            )

        return document.id

    async def _process_document(
        self, document_id: uuid.UUID, file_path: str, ext: str
    ) -> None:
        """Pipeline interno de procesamiento."""
        start = time.monotonic()

        # Step 1: OCR
        raw_text, ocr_confidence = await self._run_ocr(file_path, ext)

        # Step 2: NLP classification
        doc_type, doc_type_confidence = self._classify_document(raw_text)

        # Step 3: NLP entity extraction
        extracted_data, entities = self._extract_entities(raw_text, doc_type)

        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Step 4: Store results
        await self._doc_repo.update_processing_result(
            document_id=document_id,
            raw_text=raw_text,
            ocr_confidence=ocr_confidence,
            document_type=doc_type,
            document_type_confidence=doc_type_confidence,
            extracted_data=extracted_data,
            processing_status="completed",
            processing_time_ms=elapsed_ms,
        )

        if entities:
            await self._doc_repo.add_entities(document_id, entities)

        logger.info(
            "document_processed",
            document_id=str(document_id),
            document_type=doc_type,
            processing_time_ms=elapsed_ms,
        )

    async def _run_ocr(self, file_path: str, ext: str) -> tuple[str, float]:
        """Ejecuta OCR sobre el archivo."""
        try:
            from app.core.ocr import OCRExtractor

            extractor = OCRExtractor()
            if ext == ".pdf":
                result = extractor.extract_from_pdf(file_path)
            else:
                result = extractor.extract_from_image(file_path)
            return result.text, result.confidence
        except Exception:
            logger.warning("ocr_fallback", file_path=file_path)
            return "", 0.0

    def _classify_document(self, text: str) -> tuple[str, float]:
        """Clasifica el tipo de documento usando NLP."""
        if not text.strip():
            return "otro", 0.0
        try:
            from app.core.nlp.classifier import DocumentClassifier

            classifier = DocumentClassifier()
            result = classifier.classify(text)
            return result.document_type, result.confidence
        except Exception:
            logger.warning("classifier_fallback")
            return "otro", 0.0

    def _extract_entities(
        self, text: str, doc_type: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Extrae entidades y datos estructurados del texto."""
        if not text.strip():
            return {}, []
        try:
            from app.core.nlp.ner_extractor import MedicalNERExtractor

            extractor = MedicalNERExtractor()
            ner_entities = extractor.extract_entities(text)
            structured = extractor.extract_structured_data(text, doc_type)

            entity_dicts = [
                {
                    "entity_type": e.entity_type,
                    "entity_value": e.value,
                    "normalized_value": e.normalized_value,
                    "confidence": e.confidence,
                    "start_char": e.start_char,
                    "end_char": e.end_char,
                }
                for e in ner_entities
            ]
            return structured.structured_data, entity_dicts
        except Exception:
            logger.warning("ner_fallback")
            return {}, []

    async def get_document(self, document_id: uuid.UUID) -> Any:
        """Obtiene un documento por ID."""
        return await self._doc_repo.get_by_id(document_id)

    async def get_patient_documents(
        self,
        patient_id: uuid.UUID,
        doc_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Any], int]:
        """Lista documentos de un paciente."""
        return await self._doc_repo.list_by_patient(
            patient_id, doc_type=doc_type, page=page, page_size=page_size
        )
