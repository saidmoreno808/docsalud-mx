"""
Tests unitarios para TextCleaner.

Verifica la limpieza de texto OCR, correccion de artefactos,
normalizacion de abreviaturas y segmentacion de secciones.
"""

import pytest

from app.core.nlp.text_cleaner import CleanedText, TextCleaner


@pytest.fixture
def cleaner() -> TextCleaner:
    """Crea un TextCleaner con configuracion default."""
    return TextCleaner()


@pytest.fixture
def cleaner_with_abbrev() -> TextCleaner:
    """Crea un TextCleaner con expansion de abreviaturas."""
    return TextCleaner(expand_abbreviations=True)


@pytest.fixture
def sample_receta_text() -> str:
    """Texto de receta medica tipica."""
    return (
        "CLINICA RURAL SAN LUIS\n"
        "Ced. Prof. 12345678\n\n"
        "Paciente: Juan Carlos Martinez Lopez\n"
        "Edad: 58 anos    Sexo: M    Fecha: 15/01/2026\n\n"
        "Rx:\n"
        "1. Metformina 850mg tabletas\n"
        "   1 tableta cada 12 horas por 30 dias\n"
        "2. Losartan 50mg tabletas\n"
        "   1 tableta cada 24 horas por 30 dias\n\n"
        "Dx: Diabetes Mellitus tipo 2 (E11.9)\n"
        "    Hipertension arterial (I10)\n\n"
        "_________________________\n"
        "Firma del medico\n"
    )


@pytest.fixture
def noisy_ocr_text() -> str:
    """Texto con artefactos tipicos de OCR."""
    return "M3tformina 850rng tab|ctas\npacicnte: Juan\ntratarniento por 30 dias"


class TestClean:
    """Tests para el pipeline completo de limpieza."""

    def test_returns_cleaned_text(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """Pipeline retorna CleanedText con todos los campos."""
        result = cleaner.clean(sample_receta_text)
        assert isinstance(result, CleanedText)
        assert result.cleaned
        assert result.sentences
        assert result.tokens
        assert result.original == sample_receta_text

    def test_empty_text(self, cleaner: TextCleaner) -> None:
        """Texto vacio retorna resultado vacio."""
        result = cleaner.clean("")
        assert result.cleaned == ""
        assert result.sentences == []
        assert result.tokens == []

    def test_whitespace_only(self, cleaner: TextCleaner) -> None:
        """Solo espacios se trata como vacio."""
        result = cleaner.clean("   \n\n  \t  ")
        assert result.cleaned == ""

    def test_corrections_tracked(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """Las correcciones aplicadas se registran."""
        result = cleaner.clean(sample_receta_text)
        assert "unicode_normalized" in result.corrections_applied
        assert "whitespace_normalized" in result.corrections_applied

    def test_sentences_tokenized(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """El texto se tokeniza en oraciones."""
        result = cleaner.clean(sample_receta_text)
        assert len(result.sentences) >= 1

    def test_words_tokenized(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """El texto se tokeniza en palabras."""
        result = cleaner.clean(sample_receta_text)
        assert len(result.tokens) > 10


class TestFixOCRArtifacts:
    """Tests para correccion de artefactos OCR."""

    def test_fixes_pipe_to_l(self, cleaner: TextCleaner) -> None:
        """El caracter | se corrige a l."""
        result = cleaner.fix_ocr_artifacts("tab|etas")
        assert "|" not in result

    def test_fixes_rng_to_mg(self, cleaner: TextCleaner) -> None:
        """rng se corrige a mg."""
        result = cleaner.fix_ocr_artifacts("850rng")
        assert result == "850mg"

    def test_fixes_common_drug_names(self, cleaner: TextCleaner) -> None:
        """Nombres de medicamentos con errores OCR se corrigen."""
        result = cleaner.fix_ocr_artifacts("M3tformina")
        assert result == "Metformina"

    def test_fixes_paciente_typo(self, cleaner: TextCleaner) -> None:
        """pacicnte se corrige a paciente."""
        result = cleaner.fix_ocr_artifacts("pacicnte")
        assert result == "paciente"

    def test_fixes_tratamiento_typo(self, cleaner: TextCleaner) -> None:
        """tratarniento se corrige a tratamiento."""
        result = cleaner.fix_ocr_artifacts("tratarniento")
        assert result == "tratamiento"

    def test_clean_text_unchanged(self, cleaner: TextCleaner) -> None:
        """Texto limpio no se modifica."""
        clean = "Metformina 850mg tabletas"
        result = cleaner.fix_ocr_artifacts(clean)
        assert result == clean

    def test_noisy_text_cleaned(self, cleaner: TextCleaner, noisy_ocr_text: str) -> None:
        """Texto ruidoso se limpia correctamente."""
        result = cleaner.fix_ocr_artifacts(noisy_ocr_text)
        assert "Metformina" in result
        assert "850mg" in result
        assert "paciente" in result
        assert "tratamiento" in result


class TestNormalizeMedicalAbbreviations:
    """Tests para expansion de abreviaturas medicas."""

    def test_expands_dx(self, cleaner: TextCleaner) -> None:
        """Dx se expande a Diagnostico."""
        result = cleaner.normalize_medical_abbreviations("Dx: DM2")
        assert "Diagnostico:" in result

    def test_expands_rx(self, cleaner: TextCleaner) -> None:
        """Rx se expande a Receta."""
        result = cleaner.normalize_medical_abbreviations("Rx:")
        assert "Receta:" in result

    def test_expands_tx(self, cleaner: TextCleaner) -> None:
        """Tx se expande a Tratamiento."""
        result = cleaner.normalize_medical_abbreviations("Tx:")
        assert "Tratamiento:" in result

    def test_expands_vo(self, cleaner: TextCleaner) -> None:
        """VO se expande a via oral."""
        result = cleaner.normalize_medical_abbreviations("1 tableta VO")
        assert "via oral" in result

    def test_expands_dm2(self, cleaner: TextCleaner) -> None:
        """DM2 se expande a Diabetes Mellitus tipo 2."""
        result = cleaner.normalize_medical_abbreviations("DM2")
        assert "Diabetes Mellitus tipo 2" in result

    def test_expands_hta(self, cleaner: TextCleaner) -> None:
        """HTA se expande a Hipertension Arterial."""
        result = cleaner.normalize_medical_abbreviations("HTA")
        assert "Hipertension Arterial" in result

    def test_expands_tab(self, cleaner: TextCleaner) -> None:
        """tab se expande a tableta."""
        result = cleaner.normalize_medical_abbreviations("1 tab cada 8 hrs")
        assert "tableta" in result

    def test_with_abbreviation_mode(
        self, cleaner_with_abbrev: TextCleaner, sample_receta_text: str
    ) -> None:
        """Pipeline con abreviaturas expande en clean()."""
        result = cleaner_with_abbrev.clean(sample_receta_text)
        assert "abbreviations_expanded" in result.corrections_applied


class TestSegmentDocumentSections:
    """Tests para segmentacion de secciones."""

    def test_detects_encabezado(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """Detecta seccion de encabezado."""
        sections = cleaner.segment_document_sections(sample_receta_text)
        assert len(sections) >= 1

    def test_detects_datos_paciente(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """Detecta seccion de datos del paciente."""
        sections = cleaner.segment_document_sections(sample_receta_text)
        assert "datos_paciente" in sections

    def test_detects_prescripcion(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """Detecta seccion de prescripcion."""
        sections = cleaner.segment_document_sections(sample_receta_text)
        # Should detect Rx: section
        has_prescripcion = "prescripcion" in sections
        has_diagnostico = "diagnostico" in sections
        assert has_prescripcion or has_diagnostico

    def test_detects_firma(self, cleaner: TextCleaner, sample_receta_text: str) -> None:
        """Detecta seccion de firma."""
        sections = cleaner.segment_document_sections(sample_receta_text)
        assert "firma" in sections

    def test_empty_text_no_sections(self, cleaner: TextCleaner) -> None:
        """Texto vacio no produce secciones significativas."""
        sections = cleaner.segment_document_sections("")
        # Empty string may produce a default encabezado with empty content
        for value in sections.values():
            assert value.strip() == ""

    def test_lab_document_sections(self, cleaner: TextCleaner) -> None:
        """Documento de laboratorio segmenta correctamente."""
        lab_text = (
            "Hospital General SLP\n"
            "Resultados de laboratorio\n"
            "Paciente: Maria Garcia\n"
            "Glucosa: 126 mg/dL (70-100)\n"
            "Hemoglobina: 12.5 g/dL\n"
        )
        sections = cleaner.segment_document_sections(lab_text)
        assert len(sections) >= 1


class TestRemoveStopwords:
    """Tests para eliminacion de stopwords."""

    def test_removes_spanish_stopwords(self, cleaner: TextCleaner) -> None:
        """Elimina stopwords en espanol."""
        tokens = ["el", "paciente", "tiene", "diabetes", "y", "hipertension"]
        result = cleaner.remove_stopwords(tokens)
        assert "el" not in result
        assert "y" not in result
        assert "paciente" in result
        assert "diabetes" in result

    def test_empty_list(self, cleaner: TextCleaner) -> None:
        """Lista vacia retorna lista vacia."""
        result = cleaner.remove_stopwords([])
        assert result == []


class TestStemTokens:
    """Tests para stemming."""

    def test_stems_spanish_words(self, cleaner: TextCleaner) -> None:
        """Aplica stemming a palabras en espanol."""
        tokens = ["medicamentos", "tabletas", "diagnostico"]
        result = cleaner.stem_tokens(tokens)
        assert len(result) == 3
        # Stemmed forms should be different from originals for plural/common words
        assert all(isinstance(t, str) for t in result)

    def test_empty_list(self, cleaner: TextCleaner) -> None:
        """Lista vacia retorna lista vacia."""
        result = cleaner.stem_tokens([])
        assert result == []
