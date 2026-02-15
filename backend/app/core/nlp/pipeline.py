"""
Pipeline NLP principal para procesamiento de documentos medicos.

Orquesta la limpieza de texto, extraccion de entidades,
clasificacion de documentos y vinculacion de entidades.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.nlp.classifier import ClassificationResult, DocumentClassifier
from app.core.nlp.entity_linker import EntityLinker
from app.core.nlp.ner_extractor import ExtractionResult, MedicalEntity, MedicalNERExtractor
from app.core.nlp.text_cleaner import CleanedText, TextCleaner
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NLPResult:
    """Resultado completo del pipeline NLP."""

    cleaned_text: CleanedText
    classification: ClassificationResult
    extraction: ExtractionResult
    linked_entities: list[dict[str, Any]] = field(default_factory=list)
    processing_time_ms: int = 0
    warnings: list[str] = field(default_factory=list)


class NLPPipeline:
    """Pipeline NLP completo para documentos medicos.

    Orquesta los componentes: TextCleaner -> DocumentClassifier
    -> MedicalNERExtractor -> EntityLinker.
    """

    def __init__(
        self,
        ner_model_path: Optional[str] = None,
        classifier_model_path: Optional[str] = None,
        expand_abbreviations: bool = False,
    ) -> None:
        """Inicializa el pipeline NLP.

        Args:
            ner_model_path: Ruta al modelo NER custom.
            classifier_model_path: Ruta al modelo clasificador fine-tuned.
            expand_abbreviations: Si expandir abreviaturas en limpieza.
        """
        self.cleaner = TextCleaner(expand_abbreviations=expand_abbreviations)
        self.classifier = DocumentClassifier(model_path=classifier_model_path)
        self.ner_extractor = MedicalNERExtractor(model_path=ner_model_path)
        self.entity_linker = EntityLinker()

    def process(self, text: str, doc_type: Optional[str] = None) -> NLPResult:
        """Ejecuta el pipeline NLP completo.

        Args:
            text: Texto crudo extraido por OCR.
            doc_type: Tipo de documento (si ya se conoce). Si None, se clasifica.

        Returns:
            NLPResult con todos los resultados del pipeline.
        """
        start_time = time.perf_counter()
        warnings: list[str] = []

        # Step 1: Clean text
        cleaned = self.cleaner.clean(text)
        if not cleaned.cleaned:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return NLPResult(
                cleaned_text=cleaned,
                classification=ClassificationResult(
                    document_type="otro", confidence=0.0, model_used="empty"
                ),
                extraction=ExtractionResult(),
                processing_time_ms=elapsed_ms,
                warnings=["empty_text_after_cleaning"],
            )

        # Step 2: Classify document
        if doc_type:
            classification = ClassificationResult(
                document_type=doc_type,
                confidence=1.0,
                model_used="user_provided",
            )
        else:
            classification = self.classifier.classify(cleaned.cleaned)
            if classification.confidence < 0.6:
                warnings.append(
                    f"low_classification_confidence: {classification.confidence:.2f}"
                )

        # Step 3: Extract entities
        extraction = self.ner_extractor.extract_structured_data(
            cleaned.cleaned,
            classification.document_type,
        )

        if not extraction.entities:
            warnings.append("no_entities_extracted")

        # Step 4: Link entities to reference data
        linked = self.entity_linker.link_entities(extraction.entities)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        logger.info(
            "nlp_pipeline_completed",
            doc_type=classification.document_type,
            confidence=classification.confidence,
            entities_count=len(extraction.entities),
            linked_count=len(linked),
            processing_time_ms=elapsed_ms,
        )

        return NLPResult(
            cleaned_text=cleaned,
            classification=classification,
            extraction=extraction,
            linked_entities=linked,
            processing_time_ms=elapsed_ms,
            warnings=warnings,
        )
