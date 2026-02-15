"""
Tests unitarios para SklearnDocumentClassifier.
"""

import numpy as np
import pytest

from app.core.ml.document_classifier import (
    DOCUMENT_LABELS,
    SklearnClassificationResult,
    SklearnDocumentClassifier,
    TrainingMetrics,
)


@pytest.fixture
def training_data() -> tuple[list[str], list[str]]:
    """Datos de entrenamiento sinteticos minimos."""
    texts = [
        # Recetas
        "Metformina 850mg tabletas cada 12 horas por 30 dias Rx receta",
        "Losartan 50mg tabletas cada 24 horas receta medica dosis",
        "Omeprazol 20mg capsulas cada 24 horas via oral Rx medicamento",
        "Aspirina 100mg tableta diaria receta tratamiento",
        "Insulina 10 UI subcutanea cada 12 horas receta prescripcion",
        # Laboratorio
        "Glucosa 126 mg/dL referencia 70-100 resultado laboratorio quimica sanguinea",
        "Hemoglobina 14.2 g/dL laboratorio biometria hematica resultado",
        "Colesterol total 245 mg/dL trigliceridos 180 mg/dL laboratorio resultado",
        "Creatinina 0.9 mg/dL urea 35 mg/dL laboratorio resultado quimica",
        "Leucocitos 7500 eritrocitos 4.8 laboratorio biometria hematica",
        # Nota medica
        "Nota medica exploracion fisica signos vitales presion arterial motivo consulta",
        "Nota de evolucion interrogatorio padecimiento actual plan diagnostico",
        "Exploracion fisica nota medica subjetivo objetivo signos vitales",
        "Nota medica antecedentes motivo de consulta plan tratamiento medico",
        "Nota de evolucion control diabetes exploracion fisica signos vitales",
        # Referencia
        "Referencia segundo nivel hospital motivo de envio tratamiento previo",
        "Contrareferencia unidad de referencia se refiere paciente diagnostico",
        "Referencia hospital tercer nivel motivo envio especialidad",
        "Se refiere al segundo nivel referencia medica hospital general",
        "Referencia contrareferencia motivo de envio tratamiento previo hospital",
    ]
    labels = (
        ["receta"] * 5
        + ["laboratorio"] * 5
        + ["nota_medica"] * 5
        + ["referencia"] * 5
    )
    return texts, labels


@pytest.fixture
def trained_classifier(
    training_data: tuple[list[str], list[str]],
) -> SklearnDocumentClassifier:
    """Clasificador ya entrenado."""
    clf = SklearnDocumentClassifier()
    texts, labels = training_data
    clf.train(texts, labels, cv_folds=2)
    return clf


class TestTrain:
    def test_trains_successfully(
        self, training_data: tuple[list[str], list[str]]
    ) -> None:
        clf = SklearnDocumentClassifier()
        texts, labels = training_data
        metrics = clf.train(texts, labels, cv_folds=2)
        assert len(metrics) == 3  # 3 models
        assert clf._is_trained

    def test_selects_best_model(
        self, training_data: tuple[list[str], list[str]]
    ) -> None:
        clf = SklearnDocumentClassifier()
        texts, labels = training_data
        clf.train(texts, labels, cv_folds=2)
        assert clf._best_model_name in ["random_forest", "svm", "gradient_boosting"]

    def test_metrics_have_cv_scores(
        self, training_data: tuple[list[str], list[str]]
    ) -> None:
        clf = SklearnDocumentClassifier()
        texts, labels = training_data
        metrics = clf.train(texts, labels, cv_folds=2)
        for name, m in metrics.items():
            assert isinstance(m, TrainingMetrics)
            assert len(m.cv_scores) >= 2
            assert m.cv_mean >= 0

    def test_cv_scores_reasonable(
        self, training_data: tuple[list[str], list[str]]
    ) -> None:
        clf = SklearnDocumentClassifier()
        texts, labels = training_data
        metrics = clf.train(texts, labels, cv_folds=2)
        # At least one model should have reasonable F1
        best_f1 = max(m.cv_mean for m in metrics.values())
        assert best_f1 > 0.3


class TestPredict:
    def test_predicts_receta(
        self, trained_classifier: SklearnDocumentClassifier
    ) -> None:
        result = trained_classifier.predict(
            "Metformina 850mg tabletas cada 12 horas Rx receta"
        )
        assert isinstance(result, SklearnClassificationResult)
        assert result.document_type == "receta"

    def test_predicts_laboratorio(
        self, trained_classifier: SklearnDocumentClassifier
    ) -> None:
        result = trained_classifier.predict(
            "Glucosa 200 mg/dL resultado laboratorio quimica sanguinea"
        )
        assert result.document_type == "laboratorio"

    def test_returns_probabilities(
        self, trained_classifier: SklearnDocumentClassifier
    ) -> None:
        result = trained_classifier.predict("Rx Metformina tabletas receta")
        assert len(result.all_probabilities) >= 4
        assert sum(result.all_probabilities.values()) > 0.99

    def test_confidence_range(
        self, trained_classifier: SklearnDocumentClassifier
    ) -> None:
        result = trained_classifier.predict("texto de prueba")
        assert 0.0 <= result.confidence <= 1.0

    def test_untrained_raises(self) -> None:
        clf = SklearnDocumentClassifier()
        with pytest.raises(RuntimeError, match="not trained"):
            clf.predict("some text")


class TestPredictSingleModel:
    def test_uses_specific_model(
        self, trained_classifier: SklearnDocumentClassifier
    ) -> None:
        result = trained_classifier.predict_single_model(
            "Metformina tabletas receta Rx", "random_forest"
        )
        assert "random_forest" in result.model_used

    def test_invalid_model_raises(
        self, trained_classifier: SklearnDocumentClassifier
    ) -> None:
        with pytest.raises(ValueError, match="not found"):
            trained_classifier.predict_single_model("text", "nonexistent")


class TestSaveLoad:
    def test_save_load_preserves_predictions(
        self,
        trained_classifier: SklearnDocumentClassifier,
        tmp_path: str,
    ) -> None:
        text = "Metformina 850mg tabletas cada 12 horas Rx receta"
        original = trained_classifier.predict(text)

        trained_classifier.save(str(tmp_path))

        loaded = SklearnDocumentClassifier()
        loaded.load(str(tmp_path))
        restored = loaded.predict(text)

        assert original.document_type == restored.document_type
        assert abs(original.confidence - restored.confidence) < 0.01


class TestConfusionMatrix:
    def test_returns_matrix(
        self,
        trained_classifier: SklearnDocumentClassifier,
        training_data: tuple[list[str], list[str]],
    ) -> None:
        texts, labels = training_data
        cm = trained_classifier.get_confusion_matrix(texts, labels)
        assert isinstance(cm, np.ndarray)
        assert cm.shape[0] == cm.shape[1]
