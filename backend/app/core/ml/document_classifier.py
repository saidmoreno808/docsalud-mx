"""
Clasificador de documentos con ML tradicional (Sklearn).

Implementa ensemble de Random Forest, SVM y Gradient Boosting
para clasificar documentos medicos. Complementa al clasificador
de HuggingFace como fallback y baseline de comparacion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from app.utils.logger import get_logger

logger = get_logger(__name__)

DOCUMENT_LABELS: list[str] = [
    "receta", "laboratorio", "nota_medica", "referencia", "consentimiento", "otro",
]


@dataclass
class SklearnClassificationResult:
    """Resultado de clasificacion con Sklearn."""

    document_type: str
    confidence: float
    all_probabilities: dict[str, float] = field(default_factory=dict)
    model_used: str = "sklearn_ensemble"


@dataclass
class TrainingMetrics:
    """Metricas de entrenamiento."""

    model_name: str
    cv_scores: list[float] = field(default_factory=list)
    cv_mean: float = 0.0
    cv_std: float = 0.0
    train_f1: float = 0.0
    classification_report: str = ""


class SklearnDocumentClassifier:
    """Clasificador de documentos con ensemble de modelos Sklearn."""

    def __init__(self) -> None:
        """Inicializa los pipelines de clasificacion."""
        self.models: dict[str, Pipeline] = {
            "random_forest": Pipeline([
                ("tfidf", TfidfVectorizer(
                    max_features=5000, ngram_range=(1, 2),
                    strip_accents="unicode", sublinear_tf=True,
                )),
                ("clf", RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                )),
            ]),
            "svm": Pipeline([
                ("tfidf", TfidfVectorizer(
                    max_features=5000, ngram_range=(1, 2),
                    strip_accents="unicode", sublinear_tf=True,
                )),
                ("clf", SVC(
                    kernel="rbf",
                    probability=True,
                    class_weight="balanced",
                    random_state=42,
                )),
            ]),
            "gradient_boosting": Pipeline([
                ("tfidf", TfidfVectorizer(
                    max_features=5000, ngram_range=(1, 2),
                    strip_accents="unicode", sublinear_tf=True,
                )),
                ("clf", GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42,
                )),
            ]),
        }
        self._best_model_name: Optional[str] = None
        self._is_trained = False
        self._label_list: list[str] = DOCUMENT_LABELS

    @property
    def best_model_name(self) -> str:
        """Nombre del mejor modelo tras entrenamiento."""
        return self._best_model_name or "random_forest"

    @property
    def best_model(self) -> Pipeline:
        """Retorna el mejor pipeline entrenado."""
        return self.models[self.best_model_name]

    def train(
        self,
        texts: list[str],
        labels: list[str],
        cv_folds: int = 5,
    ) -> dict[str, TrainingMetrics]:
        """Entrena todos los modelos y retorna metricas comparativas.

        Usa cross-validation con k folds. Selecciona el mejor modelo
        por F1-score macro.

        Args:
            texts: Lista de textos de entrenamiento.
            labels: Lista de labels correspondientes.
            cv_folds: Numero de folds para cross-validation.

        Returns:
            Diccionario con metricas por modelo.
        """
        unique_labels = sorted(set(labels))
        self._label_list = unique_labels

        all_metrics: dict[str, TrainingMetrics] = {}
        best_f1 = -1.0

        for name, pipeline in self.models.items():
            logger.info("training_sklearn_model", model=name)

            actual_folds = min(cv_folds, len(texts))
            label_counts = {}
            for lbl in labels:
                label_counts[lbl] = label_counts.get(lbl, 0) + 1
            min_count = min(label_counts.values()) if label_counts else 0
            actual_folds = min(actual_folds, min_count) if min_count > 0 else 2
            actual_folds = max(actual_folds, 2)

            cv_scores = cross_val_score(
                pipeline, texts, labels,
                cv=actual_folds, scoring="f1_macro",
                n_jobs=-1,
            )

            pipeline.fit(texts, labels)
            train_preds = pipeline.predict(texts)
            train_f1 = f1_score(labels, train_preds, average="macro", zero_division=0)
            report = classification_report(labels, train_preds, zero_division=0)

            metrics = TrainingMetrics(
                model_name=name,
                cv_scores=cv_scores.tolist(),
                cv_mean=float(cv_scores.mean()),
                cv_std=float(cv_scores.std()),
                train_f1=train_f1,
                classification_report=report,
            )
            all_metrics[name] = metrics

            logger.info(
                "model_trained",
                model=name,
                cv_mean=f"{metrics.cv_mean:.4f}",
                cv_std=f"{metrics.cv_std:.4f}",
                train_f1=f"{train_f1:.4f}",
            )

            if metrics.cv_mean > best_f1:
                best_f1 = metrics.cv_mean
                self._best_model_name = name

        self._is_trained = True
        logger.info("best_model_selected", model=self._best_model_name, f1=best_f1)

        return all_metrics

    def predict(self, text: str) -> SklearnClassificationResult:
        """Predice usando ensemble soft voting.

        Promedia las probabilidades de todos los modelos entrenados
        para obtener la prediccion final.

        Args:
            text: Texto del documento a clasificar.

        Returns:
            SklearnClassificationResult con clase y probabilidades.

        Raises:
            RuntimeError: Si los modelos no han sido entrenados.
        """
        if not self._is_trained:
            raise RuntimeError("Models not trained. Call train() first.")

        all_probs: list[np.ndarray] = []

        for name, pipeline in self.models.items():
            try:
                probs = pipeline.predict_proba([text])[0]
                all_probs.append(probs)
            except Exception as e:
                logger.warning("model_predict_error", model=name, error=str(e))

        if not all_probs:
            return SklearnClassificationResult(
                document_type="otro",
                confidence=0.0,
                model_used="sklearn_ensemble_failed",
            )

        avg_probs = np.mean(all_probs, axis=0)
        predicted_idx = int(np.argmax(avg_probs))
        confidence = float(avg_probs[predicted_idx])

        prob_dict = {
            self._label_list[i]: float(avg_probs[i])
            for i in range(min(len(self._label_list), len(avg_probs)))
        }

        return SklearnClassificationResult(
            document_type=self._label_list[predicted_idx],
            confidence=confidence,
            all_probabilities=prob_dict,
            model_used=f"sklearn_ensemble(best={self.best_model_name})",
        )

    def predict_single_model(
        self, text: str, model_name: str
    ) -> SklearnClassificationResult:
        """Predice usando un modelo especifico.

        Args:
            text: Texto del documento.
            model_name: Nombre del modelo a usar.

        Returns:
            SklearnClassificationResult.
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available: {list(self.models)}")

        pipeline = self.models[model_name]
        probs = pipeline.predict_proba([text])[0]
        predicted_idx = int(np.argmax(probs))

        prob_dict = {
            self._label_list[i]: float(probs[i])
            for i in range(min(len(self._label_list), len(probs)))
        }

        return SklearnClassificationResult(
            document_type=self._label_list[predicted_idx],
            confidence=float(probs[predicted_idx]),
            all_probabilities=prob_dict,
            model_used=f"sklearn_{model_name}",
        )

    def get_confusion_matrix(
        self, texts: list[str], labels: list[str]
    ) -> np.ndarray:
        """Calcula confusion matrix del best model.

        Args:
            texts: Textos de evaluacion.
            labels: Labels verdaderos.

        Returns:
            Confusion matrix como numpy array.
        """
        preds = self.best_model.predict(texts)
        return confusion_matrix(labels, preds, labels=self._label_list)

    def save(self, path: str) -> None:
        """Serializa modelos entrenados con joblib.

        Args:
            path: Ruta del directorio de salida.
        """
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        for name, pipeline in self.models.items():
            joblib.dump(pipeline, save_dir / f"{name}.joblib")

        metadata = {
            "best_model": self._best_model_name,
            "labels": self._label_list,
            "is_trained": self._is_trained,
        }
        joblib.dump(metadata, save_dir / "metadata.joblib")

        logger.info("sklearn_models_saved", path=path)

    def load(self, path: str) -> None:
        """Carga modelos serializados.

        Args:
            path: Ruta del directorio con los modelos.
        """
        load_dir = Path(path)

        for name in list(self.models.keys()):
            model_path = load_dir / f"{name}.joblib"
            if model_path.exists():
                self.models[name] = joblib.load(model_path)

        metadata_path = load_dir / "metadata.joblib"
        if metadata_path.exists():
            metadata = joblib.load(metadata_path)
            self._best_model_name = metadata.get("best_model")
            self._label_list = metadata.get("labels", DOCUMENT_LABELS)
            self._is_trained = metadata.get("is_trained", True)

        logger.info("sklearn_models_loaded", path=path)
