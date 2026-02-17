"""
Limpieza y normalizacion de texto OCR usando NLTK.

Proporciona pipeline de limpieza optimizado para texto extraido
de expedientes clinicos mexicanos mediante OCR.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Ensure NLTK data is available
for resource in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)


@dataclass
class CleanedText:
    """Resultado de la limpieza de texto."""

    original: str
    cleaned: str
    sentences: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)
    sections: dict[str, str] = field(default_factory=dict)
    corrections_applied: list[str] = field(default_factory=list)


# Mapeo de artefactos OCR comunes en documentos medicos
OCR_ARTIFACT_MAP: dict[str, str] = {
    r"\|": "l",
    r"(?<=[a-zA-Z])0(?=[a-zA-Z])": "o",
    r"(?<=[a-zA-Z])1(?=[a-zA-Z])": "l",
    r"rn(?=[a-z])": "m",
    r"(?<=\d)\.(?=\d{3}\b)": "",
    r"(?<=\w),,(?=\w)": ",",
    r"\brng\b": "mg",
    r"\brng/dL\b": "mg/dL",
    r"\btablctas\b": "tabletas",
    r"\bcapsulas\b": "capsulas",
    r"\bjarabe\b": "jarabe",
    r"\bpacicnte\b": "paciente",
    r"\bmedicarnento\b": "medicamento",
    r"\bdiagnostico\b": "diagnostico",
    r"\btratarniento\b": "tratamiento",
    r"\bhipertensi6n\b": "hipertension",
    r"\bdiab[e3]tes\b": "diabetes",
    r"\bM[e3]tformina\b": "Metformina",
    r"\bLosart[a@]n\b": "Losartan",
    r"\bGlib[e3]nclamida\b": "Glibenclamida",
    r"\bOmepraz[o0]l\b": "Omeprazol",
}

# Abreviaturas medicas comunes en Mexico
MEDICAL_ABBREVIATIONS: dict[str, str] = {
    r"\bDx\b\.?:?": "Diagnostico:",
    r"\bDX\b\.?:?": "Diagnostico:",
    r"\bTx\b\.?:?": "Tratamiento:",
    r"\bTX\b\.?:?": "Tratamiento:",
    r"\bRx\b\.?:?": "Receta:",
    r"\bRX\b\.?:?": "Receta:",
    r"\bHx\b\.?:?": "Historia:",
    r"\bSx\b\.?:?": "Sintomas:",
    r"\bEF\b\.?:?": "Exploracion Fisica:",
    r"\bSV\b\.?:?": "Signos Vitales:",
    r"\bTA\b(?=\s*:?\s*\d)": "Tension Arterial",
    r"\bFC\b(?=\s*:?\s*\d)": "Frecuencia Cardiaca",
    r"\bFR\b(?=\s*:?\s*\d)": "Frecuencia Respiratoria",
    r"\bT\b(?=\s*:?\s*\d+\.?\d*\s*[°gG])": "Temperatura",
    r"\bVO\b": "via oral",
    r"\bIM\b(?=\s)": "intramuscular",
    r"\bIV\b(?=\s)": "intravenosa",
    r"\bSC\b(?=\s)": "subcutanea",
    r"\bc/\s*(\d)": r"cada \1",
    r"\bh\b(?=\s*(?:por|durante|x))": "horas",
    r"\bhr?s\b": "horas",
    r"\bmin\b": "minutos",
    r"\bsem\b": "semanas",
    r"\bDM2?\b": "Diabetes Mellitus tipo 2",
    r"\bHTA\b": "Hipertension Arterial",
    r"\bIRC\b": "Insuficiencia Renal Cronica",
    r"\bEPOC\b": "Enfermedad Pulmonar Obstructiva Cronica",
    r"\bIVU\b": "Infeccion de Vias Urinarias",
    r"\bITU\b": "Infeccion del Tracto Urinario",
    r"\bEVC\b": "Evento Vascular Cerebral",
    r"\bIAM\b": "Infarto Agudo de Miocardio",
    r"\bBHC\b": "Biometria Hematica Completa",
    r"\bQS\b": "Quimica Sanguinea",
    r"\bEGO\b": "Examen General de Orina",
    r"\btab\b\.?": "tableta",
    r"\btabs\b\.?": "tabletas",
    r"\bcap\b\.?": "capsula",
    r"\bcaps\b\.?": "capsulas",
    r"\bamp\b\.?": "ampolleta",
    r"\bsol\b\.?(?=\s+(?:iny|oral))": "solucion",
    r"\bsusp\b\.?": "suspension",
    r"\bCed\b\.?\s*Prof\b\.?": "Cedula Profesional",
}

# Patrones de seccion de documento
SECTION_PATTERNS: dict[str, list[str]] = {
    "encabezado": [
        r"(?i)cl[ií]nica\s+\w+",
        r"(?i)hospital\s+\w+",
        r"(?i)consultorio\s+\w+",
        r"(?i)centro\s+de\s+salud",
        r"(?i)c[ée]dula\s+profesional",
    ],
    "datos_paciente": [
        r"(?i)paciente\s*:",
        r"(?i)nombre\s*:",
        r"(?i)edad\s*:",
        r"(?i)sexo\s*:",
        r"(?i)fecha\s*de\s*nacimiento",
        r"(?i)CURP\s*:",
    ],
    "prescripcion": [
        r"(?i)(?:Rx|Receta)\s*:",
        r"(?i)\d+\.\s*\w+\s+\d+\s*mg",
        r"(?i)tabletas?\b",
        r"(?i)cada\s+\d+\s+horas",
    ],
    "diagnostico": [
        r"(?i)(?:Dx|Diagn[oó]stico)\s*:",
        r"(?i)[A-Z]\d{2}\.?\d*",
    ],
    "laboratorio": [
        r"(?i)resultados?\s+de\s+laboratorio",
        r"(?i)glucosa\s*:",
        r"(?i)hemoglobina\s*:",
        r"(?i)colesterol\s*:",
        r"(?i)mg/dL",
        r"(?i)g/dL",
    ],
    "signos_vitales": [
        r"(?i)signos?\s+vitales?\s*:",
        r"(?i)(?:TA|[Tt]ensi[oó]n)\s*:\s*\d+/\d+",
        r"(?i)(?:FC|[Ff]recuencia)\s*:\s*\d+",
        r"(?i)(?:T|[Tt]emp)\s*:\s*\d+",
    ],
    "firma": [
        r"(?i)firma\s+del?\s+m[eé]dico",
        r"_{5,}",
        r"(?i)Dr\.?\s+\w+",
        r"(?i)m[eé]dico\s+tratante",
    ],
}


class TextCleaner:
    """Limpieza de texto extraido por OCR de documentos medicos."""

    def __init__(self, expand_abbreviations: bool = False) -> None:
        """Inicializa el TextCleaner.

        Args:
            expand_abbreviations: Si True, expande abreviaturas medicas
                en el texto limpio. Default False para preservar formato original.
        """
        self.stemmer = SnowballStemmer("spanish")
        self.stop_words = set(stopwords.words("spanish"))
        self.expand_abbreviations = expand_abbreviations

    def clean(self, text: str) -> CleanedText:
        """Pipeline completo de limpieza de texto OCR.

        Pasos:
        1. Normalizar unicode y encoding
        2. Corregir artefactos comunes de OCR
        3. Normalizar espacios y saltos de linea
        4. Expandir abreviaturas (si configurado)
        5. Tokenizar en oraciones y palabras
        6. Identificar secciones del documento

        Args:
            text: Texto crudo extraido por OCR.

        Returns:
            CleanedText con texto limpio, tokens, oraciones y secciones.
        """
        if not text or not text.strip():
            return CleanedText(
                original=text,
                cleaned="",
                sentences=[],
                tokens=[],
                sections={},
                corrections_applied=[],
            )

        corrections: list[str] = []
        cleaned = text

        cleaned = self._normalize_unicode(cleaned)
        corrections.append("unicode_normalized")

        cleaned_after_ocr = self.fix_ocr_artifacts(cleaned)
        if cleaned_after_ocr != cleaned:
            corrections.append("ocr_artifacts_fixed")
        cleaned = cleaned_after_ocr

        cleaned = self._normalize_whitespace(cleaned)
        corrections.append("whitespace_normalized")

        if self.expand_abbreviations:
            cleaned_after_abbr = self.normalize_medical_abbreviations(cleaned)
            if cleaned_after_abbr != cleaned:
                corrections.append("abbreviations_expanded")
            cleaned = cleaned_after_abbr

        sentences = self._tokenize_sentences(cleaned)
        tokens = self._tokenize_words(cleaned)
        sections = self.segment_document_sections(cleaned)

        logger.debug(
            "text_cleaned",
            original_length=len(text),
            cleaned_length=len(cleaned),
            sentences_count=len(sentences),
            tokens_count=len(tokens),
            sections_found=list(sections.keys()),
            corrections=corrections,
        )

        return CleanedText(
            original=text,
            cleaned=cleaned,
            sentences=sentences,
            tokens=tokens,
            sections=sections,
            corrections_applied=corrections,
        )

    def fix_ocr_artifacts(self, text: str) -> str:
        """Corrige errores comunes de OCR en documentos medicos.

        Aplica patrones regex para corregir sustituciones tipicas
        de caracteres que Tesseract produce en documentos escaneados.

        Args:
            text: Texto con posibles artefactos OCR.

        Returns:
            Texto con artefactos corregidos.
        """
        result = text
        for pattern, replacement in OCR_ARTIFACT_MAP.items():
            result = re.sub(pattern, replacement, result)
        return result

    def normalize_medical_abbreviations(self, text: str) -> str:
        """Expande abreviaturas medicas comunes.

        Convierte abreviaturas como Dx, Tx, Rx, VO, etc. a
        sus formas completas en espanol.

        Args:
            text: Texto con abreviaturas medicas.

        Returns:
            Texto con abreviaturas expandidas.
        """
        result = text
        for pattern, replacement in MEDICAL_ABBREVIATIONS.items():
            result = re.sub(pattern, replacement, result)
        return result

    def segment_document_sections(self, text: str) -> dict[str, str]:
        """Identifica y extrae secciones del documento.

        Busca patrones caracteristicos de cada seccion en el texto
        y extrae el contenido correspondiente.

        Args:
            text: Texto limpio del documento.

        Returns:
            Diccionario con nombre de seccion como key y contenido como value.
        """
        sections: dict[str, str] = {}
        lines = text.split("\n")

        current_section: Optional[str] = None
        current_content: list[str] = []

        for line in lines:
            detected_section = self._detect_section(line)

            if detected_section and detected_section != current_section:
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = detected_section
                current_content = [line]
            elif current_section:
                current_content.append(line)
            else:
                current_content.append(line)
                current_section = "encabezado"

        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def remove_stopwords(self, tokens: list[str]) -> list[str]:
        """Elimina stopwords de una lista de tokens.

        Args:
            tokens: Lista de tokens.

        Returns:
            Lista de tokens sin stopwords.
        """
        return [t for t in tokens if t.lower() not in self.stop_words and len(t) > 1]

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        """Aplica stemming a una lista de tokens.

        Args:
            tokens: Lista de tokens.

        Returns:
            Lista de tokens con stemming aplicado.
        """
        return [self.stemmer.stem(t) for t in tokens]

    def _normalize_unicode(self, text: str) -> str:
        """Normaliza caracteres unicode y encoding."""
        text = unicodedata.normalize("NFKC", text)
        replacements = {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u2026": "...",
            "\u00a0": " ",
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normaliza espacios y saltos de linea."""
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" +\n", "\n", text)
        text = re.sub(r"\n +", "\n", text)
        return text.strip()

    def _tokenize_sentences(self, text: str) -> list[str]:
        """Tokeniza texto en oraciones usando NLTK."""
        try:
            sentences = sent_tokenize(text, language="spanish")
        except Exception:
            sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        return sentences

    def _tokenize_words(self, text: str) -> list[str]:
        """Tokeniza texto en palabras usando NLTK."""
        try:
            tokens = word_tokenize(text, language="spanish")
        except Exception:
            tokens = text.split()
        return tokens

    def _detect_section(self, line: str) -> Optional[str]:
        """Detecta a que seccion pertenece una linea."""
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line):
                    return section_name
        return None
