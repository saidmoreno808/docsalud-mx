"""
Tests unitarios para MedicalNERExtractor.

Verifica la extraccion de entidades medicas del texto
de documentos clinicos.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.nlp.ner_extractor import (
    ExtractionResult,
    MedicalEntity,
    MedicalNERExtractor,
)


@pytest.fixture
def extractor() -> MedicalNERExtractor:
    """Crea un NER extractor con modelo base."""
    return MedicalNERExtractor()


@pytest.fixture
def sample_receta() -> str:
    """Texto de receta medica."""
    return (
        "Paciente: Juan Carlos Martinez Lopez\n"
        "Fecha: 15/01/2026\n\n"
        "Rx:\n"
        "1. Metformina 850mg tabletas\n"
        "   1 tableta cada 12 horas por 30 dias\n"
        "2. Losartan 50mg tabletas\n"
        "   1 tableta cada 24 horas por 30 dias\n\n"
        "Dx: Diabetes Mellitus tipo 2 (E11.9)\n"
        "    Hipertension arterial (I10)\n"
    )


@pytest.fixture
def sample_laboratorio() -> str:
    """Texto de resultados de laboratorio."""
    return (
        "Resultados de laboratorio\n"
        "Fecha: 10/01/2026\n\n"
        "Glucosa: 126 mg/dL (70-100 mg/dL)\n"
        "Hemoglobina: 14.2 g/dL (12-16 g/dL)\n"
        "Colesterol total: 245 mg/dL (hasta 200 mg/dL)\n"
        "Creatinina: 0.9 mg/dL (0.7-1.2 mg/dL)\n"
    )


class TestExtractEntities:
    """Tests para extraccion de entidades."""

    def test_extracts_medications(self, extractor: MedicalNERExtractor, sample_receta: str) -> None:
        """Extrae medicamentos del texto."""
        entities = extractor.extract_entities(sample_receta)
        med_entities = [e for e in entities if e.entity_type == "MEDICAMENTO"]
        med_values = [e.value for e in med_entities]
        assert any("Metformina" in v for v in med_values) or any(
            "metformina" in v.lower() for v in med_values
        )

    def test_extracts_cie10_codes(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Extrae codigos CIE-10."""
        entities = extractor.extract_entities(sample_receta)
        cie10 = [e for e in entities if e.entity_type == "CODIGO_CIE10"]
        codes = [e.value for e in cie10]
        assert "E11.9" in codes or "I10" in codes

    def test_extracts_doses(self, extractor: MedicalNERExtractor, sample_receta: str) -> None:
        """Extrae dosis de medicamentos."""
        entities = extractor.extract_entities(sample_receta)
        doses = [e for e in entities if e.entity_type == "DOSIS"]
        assert len(doses) >= 1

    def test_extracts_dates(self, extractor: MedicalNERExtractor, sample_receta: str) -> None:
        """Extrae fechas del documento."""
        entities = extractor.extract_entities(sample_receta)
        dates = [e for e in entities if e.entity_type == "FECHA"]
        assert len(dates) >= 1
        assert any("15/01/2026" in e.value for e in dates)

    def test_extracts_frequencies(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Extrae frecuencias de toma."""
        entities = extractor.extract_entities(sample_receta)
        freq = [e for e in entities if e.entity_type == "FRECUENCIA_TIEMPO"]
        assert len(freq) >= 1

    def test_extracts_durations(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Extrae duracion del tratamiento."""
        entities = extractor.extract_entities(sample_receta)
        dur = [e for e in entities if e.entity_type == "DURACION"]
        assert len(dur) >= 1

    def test_extracts_presentations(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Extrae presentacion del medicamento."""
        entities = extractor.extract_entities(sample_receta)
        pres = [e for e in entities if e.entity_type == "PRESENTACION"]
        assert len(pres) >= 1

    def test_extracts_lab_values(
        self, extractor: MedicalNERExtractor, sample_laboratorio: str
    ) -> None:
        """Extrae valores de laboratorio."""
        entities = extractor.extract_entities(sample_laboratorio)
        values = [e for e in entities if e.entity_type == "VALOR_MEDICION"]
        assert len(values) >= 1

    def test_extracts_reference_ranges(
        self, extractor: MedicalNERExtractor, sample_laboratorio: str
    ) -> None:
        """Extrae rangos de referencia."""
        entities = extractor.extract_entities(sample_laboratorio)
        ranges = [e for e in entities if e.entity_type == "RANGO_REFERENCIA"]
        assert len(ranges) >= 1

    def test_empty_text_returns_empty(self, extractor: MedicalNERExtractor) -> None:
        """Texto vacio retorna lista vacia."""
        entities = extractor.extract_entities("")
        assert entities == []

    def test_entities_have_positions(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Las entidades tienen posiciones de caracteres."""
        entities = extractor.extract_entities(sample_receta)
        for ent in entities:
            assert ent.start_char >= 0
            assert ent.end_char > ent.start_char

    def test_entities_have_confidence(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Las entidades tienen score de confianza."""
        entities = extractor.extract_entities(sample_receta)
        for ent in entities:
            assert 0.0 <= ent.confidence <= 1.0

    def test_entities_sorted_by_position(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Las entidades estan ordenadas por posicion."""
        entities = extractor.extract_entities(sample_receta)
        if len(entities) > 1:
            for i in range(len(entities) - 1):
                assert entities[i].start_char <= entities[i + 1].start_char


class TestExtractStructuredData:
    """Tests para extraccion de datos estructurados."""

    def test_receta_has_medications(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Receta extrae medicamentos estructurados."""
        result = extractor.extract_structured_data(sample_receta, "receta")
        assert isinstance(result, ExtractionResult)
        meds = result.structured_data.get("medicamentos", [])
        assert len(meds) >= 1

    def test_receta_has_diagnosis(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Receta extrae diagnostico."""
        result = extractor.extract_structured_data(sample_receta, "receta")
        # Either has diagnosis directly or via CIE-10
        dx = result.structured_data.get("diagnostico")
        cie = result.structured_data.get("codigo_cie10")
        assert dx is not None or cie is not None

    def test_laboratorio_has_results(
        self, extractor: MedicalNERExtractor, sample_laboratorio: str
    ) -> None:
        """Laboratorio extrae resultados."""
        result = extractor.extract_structured_data(sample_laboratorio, "laboratorio")
        resultados = result.structured_data.get("resultados", [])
        assert len(resultados) >= 1

    def test_result_has_processing_time(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Resultado incluye tiempo de procesamiento."""
        result = extractor.extract_structured_data(sample_receta, "receta")
        assert result.processing_time_ms >= 0

    def test_result_has_model_name(
        self, extractor: MedicalNERExtractor, sample_receta: str
    ) -> None:
        """Resultado incluye nombre del modelo usado."""
        result = extractor.extract_structured_data(sample_receta, "receta")
        assert result.model_used

    def test_generic_extraction(self, extractor: MedicalNERExtractor, sample_receta: str) -> None:
        """Tipo desconocido usa extraccion generica."""
        result = extractor.extract_structured_data(sample_receta, "unknown_type")
        assert isinstance(result.structured_data, dict)

    def test_nota_medica_extraction(self, extractor: MedicalNERExtractor) -> None:
        """Nota medica extrae datos estructurados."""
        text = (
            "Nota medica\n"
            "Paciente: Ana Rodriguez\n"
            "Fecha: 12/01/2026\n"
            "Dx: Hipertension arterial (I10)\n"
            "Tension Arterial: 140/90 mmHg\n"
            "Plan: Losartan 50mg cada 24 horas\n"
        )
        result = extractor.extract_structured_data(text, "nota_medica")
        assert "diagnostico" in result.structured_data


class TestMedicalEntity:
    """Tests para la dataclass MedicalEntity."""

    def test_create_entity(self) -> None:
        """Se puede crear una entidad medica."""
        entity = MedicalEntity(
            entity_type="MEDICAMENTO",
            value="Metformina",
            confidence=0.95,
            start_char=10,
            end_char=20,
        )
        assert entity.entity_type == "MEDICAMENTO"
        assert entity.value == "Metformina"
        assert entity.confidence == 0.95

    def test_default_values(self) -> None:
        """Valores default son correctos."""
        entity = MedicalEntity(entity_type="DOSIS", value="850mg")
        assert entity.confidence == 0.0
        assert entity.start_char == 0
        assert entity.end_char == 0
        assert entity.normalized_value is None
        assert entity.metadata == {}
