"""
Modulo NLP de DocSalud MX.

Proporciona pipeline completo de procesamiento de lenguaje natural
para documentos medicos: limpieza de texto, extraccion de entidades,
clasificacion de documentos y vinculacion a catalogos de referencia.
"""

from app.core.nlp.classifier import ClassificationResult, DocumentClassifier
from app.core.nlp.entity_linker import EntityLinker
from app.core.nlp.ner_extractor import ExtractionResult, MedicalEntity, MedicalNERExtractor
from app.core.nlp.pipeline import NLPPipeline, NLPResult
from app.core.nlp.text_cleaner import CleanedText, TextCleaner

__all__ = [
    "TextCleaner",
    "CleanedText",
    "MedicalNERExtractor",
    "MedicalEntity",
    "ExtractionResult",
    "DocumentClassifier",
    "ClassificationResult",
    "EntityLinker",
    "NLPPipeline",
    "NLPResult",
]
