"""
Modulo ML de DocSalud MX.

Proporciona clasificacion supervisada, deteccion de anomalias,
clustering de riesgo y clasificacion con transformers para
documentos medicos.
"""

from app.core.ml.document_classifier import (
    SklearnClassificationResult,
    SklearnDocumentClassifier,
    TrainingMetrics,
)
from app.core.ml.feature_engineering import FeatureEngineer, FeatureSet
from app.core.ml.model_registry import ModelInfo, ModelRegistry
from app.core.ml.risk_clusterer import ClusterDescription, ClusteringResult, RiskClusterer

__all__ = [
    "FeatureEngineer",
    "FeatureSet",
    "SklearnDocumentClassifier",
    "SklearnClassificationResult",
    "TrainingMetrics",
    "RiskClusterer",
    "ClusteringResult",
    "ClusterDescription",
    "ModelRegistry",
    "ModelInfo",
]
