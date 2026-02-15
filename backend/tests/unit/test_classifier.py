"""
Tests unitarios para DocumentClassifier.

Verifica la clasificacion heuristica de documentos medicos
(tests del modelo fine-tuned requieren GPU/modelo descargado).
"""

import pytest

from app.core.nlp.classifier import (
    ClassificationResult,
    DocumentClassifier,
    DOCUMENT_LABELS,
    LABEL_TO_ID,
)


@pytest.fixture
def classifier() -> DocumentClassifier:
    """Crea un clasificador sin modelo fine-tuned (usa heuristica)."""
    return DocumentClassifier()


@pytest.fixture
def receta_text() -> str:
    """Texto tipico de receta medica."""
    return (
        "Rx:\n"
        "1. Metformina 850mg tabletas\n"
        "   1 tableta cada 12 horas por 30 dias\n"
        "2. Losartan 50mg tabletas\n"
        "   1 tableta cada 24 horas por 30 dias\n"
        "Dx: Diabetes Mellitus tipo 2\n"
    )


@pytest.fixture
def laboratorio_text() -> str:
    """Texto tipico de resultados de laboratorio."""
    return (
        "Resultados de laboratorio\n"
        "Quimica Sanguinea\n"
        "Glucosa: 126 mg/dL (70-100 mg/dL)\n"
        "Colesterol total: 245 mg/dL\n"
        "Trigliceridos: 180 mg/dL\n"
        "Creatinina: 0.9 mg/dL (0.7-1.2 mg/dL)\n"
        "Urea: 35 mg/dL\n"
    )


@pytest.fixture
def nota_medica_text() -> str:
    """Texto tipico de nota medica."""
    return (
        "Nota medica - Nota de evolucion\n"
        "Motivo de consulta: Control de diabetes\n"
        "Interrogatorio: Paciente refiere mareo ocasional\n"
        "Exploracion fisica:\n"
        "Signos vitales: TA 130/85 mmHg, FC 78 lpm\n"
        "Diagnostico: DM2 descontrolada\n"
        "Plan: Ajuste de dosis de Metformina\n"
    )


@pytest.fixture
def referencia_text() -> str:
    """Texto tipico de referencia medica."""
    return (
        "Referencia medica\n"
        "Motivo de envio: Paciente con diabetes descontrolada\n"
        "Se refiere al segundo nivel de atencion\n"
        "Hospital de referencia: Hospital General SLP\n"
        "Tratamiento previo: Metformina 850mg cada 12 horas\n"
        "Diagnostico: E11.9 Diabetes Mellitus tipo 2\n"
    )


class TestClassify:
    """Tests para clasificacion de documentos."""

    def test_classify_receta(self, classifier: DocumentClassifier, receta_text: str) -> None:
        """Receta se clasifica correctamente."""
        result = classifier.classify(receta_text)
        assert isinstance(result, ClassificationResult)
        assert result.document_type == "receta"
        assert result.confidence > 0.3

    def test_classify_laboratorio(
        self, classifier: DocumentClassifier, laboratorio_text: str
    ) -> None:
        """Resultados de laboratorio se clasifican correctamente."""
        result = classifier.classify(laboratorio_text)
        assert result.document_type == "laboratorio"
        assert result.confidence > 0.3

    def test_classify_nota_medica(
        self, classifier: DocumentClassifier, nota_medica_text: str
    ) -> None:
        """Nota medica se clasifica correctamente."""
        result = classifier.classify(nota_medica_text)
        assert result.document_type == "nota_medica"
        assert result.confidence > 0.3

    def test_classify_referencia(
        self, classifier: DocumentClassifier, referencia_text: str
    ) -> None:
        """Referencia medica se clasifica correctamente."""
        result = classifier.classify(referencia_text)
        assert result.document_type == "referencia"
        assert result.confidence > 0.3

    def test_classify_empty_text(self, classifier: DocumentClassifier) -> None:
        """Texto vacio retorna 'otro' con confianza 0."""
        result = classifier.classify("")
        assert result.document_type == "otro"
        assert result.confidence == 0.0

    def test_classify_unknown_text(self, classifier: DocumentClassifier) -> None:
        """Texto no medico retorna 'otro'."""
        result = classifier.classify("El clima hoy esta soleado en la ciudad")
        assert result.document_type == "otro"

    def test_result_has_all_probabilities(
        self, classifier: DocumentClassifier, receta_text: str
    ) -> None:
        """Resultado incluye probabilidades de todas las clases."""
        result = classifier.classify(receta_text)
        assert len(result.all_probabilities) >= len(DOCUMENT_LABELS)

    def test_probabilities_sum_to_one(
        self, classifier: DocumentClassifier, receta_text: str
    ) -> None:
        """Probabilidades suman aproximadamente 1."""
        result = classifier.classify(receta_text)
        total = sum(result.all_probabilities.values())
        assert abs(total - 1.0) < 0.01

    def test_result_has_model_name(
        self, classifier: DocumentClassifier, receta_text: str
    ) -> None:
        """Resultado indica modelo usado."""
        result = classifier.classify(receta_text)
        assert result.model_used == "heuristic"

    def test_result_has_processing_time(
        self, classifier: DocumentClassifier, receta_text: str
    ) -> None:
        """Resultado tiene tiempo de procesamiento."""
        result = classifier.classify(receta_text)
        assert result.processing_time_ms >= 0

    def test_confidence_capped(self, classifier: DocumentClassifier, receta_text: str) -> None:
        """Confianza heuristica se limita a 0.95."""
        result = classifier.classify(receta_text)
        assert result.confidence <= 0.95


class TestClassificationResult:
    """Tests para la dataclass ClassificationResult."""

    def test_create_result(self) -> None:
        """Se puede crear un resultado de clasificacion."""
        result = ClassificationResult(
            document_type="receta",
            confidence=0.94,
            all_probabilities={"receta": 0.94, "otro": 0.06},
            model_used="heuristic",
        )
        assert result.document_type == "receta"
        assert result.confidence == 0.94


class TestLabels:
    """Tests para constantes de labels."""

    def test_labels_complete(self) -> None:
        """Todos los labels esperados estan definidos."""
        expected = {"receta", "laboratorio", "nota_medica", "referencia", "consentimiento", "otro"}
        assert set(DOCUMENT_LABELS.values()) == expected

    def test_label_to_id_inverse(self) -> None:
        """LABEL_TO_ID es inverso de DOCUMENT_LABELS."""
        for idx, label in DOCUMENT_LABELS.items():
            assert LABEL_TO_ID[label] == idx

    def test_six_classes(self) -> None:
        """Hay exactamente 6 clases."""
        assert len(DOCUMENT_LABELS) == 6
