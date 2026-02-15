"""
Extractor de entidades nombradas medicas con SpaCy.

Usa modelo base es_core_news_lg con entrenamiento custom
para extraer entidades de documentos medicos mexicanos.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import spacy
from spacy.language import Language
from spacy.tokens import DocBin

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Etiquetas NER personalizadas para documentos medicos
MEDICAL_NER_LABELS: list[str] = [
    "MEDICAMENTO",
    "DOSIS",
    "PRESENTACION",
    "FRECUENCIA_DOSIS",
    "FRECUENCIA_TIEMPO",
    "DURACION",
    "DIAGNOSTICO",
    "CODIGO_CIE10",
    "SIGNO_VITAL",
    "VALOR_MEDICION",
    "RANGO_REFERENCIA",
    "NOMBRE_PACIENTE",
    "NOMBRE_MEDICO",
    "FECHA",
    "INSTITUCION",
]


@dataclass
class MedicalEntity:
    """Entidad medica extraida del texto."""

    entity_type: str
    value: str
    normalized_value: Optional[str] = None
    confidence: float = 0.0
    start_char: int = 0
    end_char: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Resultado de extraccion de entidades."""

    entities: list[MedicalEntity] = field(default_factory=list)
    structured_data: dict[str, Any] = field(default_factory=dict)
    processing_time_ms: int = 0
    model_used: str = ""


class MedicalNERExtractor:
    """Extractor NER especializado en documentos medicos mexicanos."""

    def __init__(self, model_path: Optional[str] = None) -> None:
        """Carga modelo SpaCy.

        Si model_path apunta a un modelo custom entrenado, lo usa.
        Si no, usa es_core_news_lg como base con reglas pattern-based.

        Args:
            model_path: Ruta al modelo SpaCy custom. Si None, usa base.
        """
        self.model_path = model_path
        self._nlp: Optional[Language] = None
        self._is_custom = False

    @property
    def nlp(self) -> Language:
        """Lazy-load del modelo SpaCy."""
        if self._nlp is None:
            self._nlp = self._load_model()
        return self._nlp

    def _load_model(self) -> Language:
        """Carga el modelo SpaCy apropiado."""
        if self.model_path and Path(self.model_path).exists():
            logger.info("loading_custom_ner_model", path=self.model_path)
            self._is_custom = True
            return spacy.load(self.model_path)

        logger.info("loading_base_spacy_model", model="es_core_news_lg")
        try:
            nlp = spacy.load("es_core_news_lg")
        except OSError:
            logger.warning("es_core_news_lg_not_found_using_small")
            try:
                nlp = spacy.load("es_core_news_sm")
            except OSError:
                logger.warning("no_spanish_model_using_blank")
                nlp = spacy.blank("es")

        self._add_pattern_rules(nlp)
        self._is_custom = False
        return nlp

    def _add_pattern_rules(self, nlp: Language) -> None:
        """Agrega reglas pattern-based al pipeline para entidades medicas."""
        if "entity_ruler" not in nlp.pipe_names:
            ruler = nlp.add_pipe("entity_ruler", before="ner" if "ner" in nlp.pipe_names else None)
        else:
            ruler = nlp.get_pipe("entity_ruler")

        patterns = self._build_medication_patterns()
        patterns.extend(self._build_diagnosis_patterns())
        patterns.extend(self._build_measurement_patterns())
        patterns.extend(self._build_date_patterns())

        ruler.add_patterns(patterns)

    def _build_medication_patterns(self) -> list[dict[str, Any]]:
        """Construye patrones para medicamentos comunes."""
        medications = [
            "Metformina", "Losartan", "Glibenclamida", "Omeprazol",
            "Enalapril", "Amlodipino", "Atorvastatina", "Aspirina",
            "Captopril", "Metoprolol", "Insulina", "Ranitidina",
            "Amoxicilina", "Ciprofloxacino", "Diclofenaco", "Paracetamol",
            "Ibuprofeno", "Naproxeno", "Prednisona", "Salbutamol",
            "Beclometasona", "Furosemida", "Hidroclorotiazida", "Clopidogrel",
            "Simvastatina", "Bezafibrato", "Nifedipino", "Verapamilo",
        ]
        patterns = []
        for med in medications:
            patterns.append({"label": "MEDICAMENTO", "pattern": med})
            patterns.append({"label": "MEDICAMENTO", "pattern": med.lower()})
        return patterns

    def _build_diagnosis_patterns(self) -> list[dict[str, Any]]:
        """Construye patrones para diagnosticos comunes."""
        diagnoses = [
            [{"LOWER": "diabetes"}, {"LOWER": "mellitus"}],
            [{"LOWER": "diabetes"}, {"LOWER": "mellitus"}, {"LOWER": "tipo"}, {"LOWER": "2"}],
            [{"LOWER": "hipertension"}, {"LOWER": "arterial"}],
            [{"LOWER": "insuficiencia"}, {"LOWER": "renal"}],
            [{"LOWER": "infeccion"}, {"LOWER": "de"}, {"LOWER": "vias"}, {"LOWER": "urinarias"}],
            [{"LOWER": "gastritis"}],
            [{"LOWER": "anemia"}],
            [{"LOWER": "hipotiroidismo"}],
            [{"LOWER": "obesidad"}],
            [{"LOWER": "dislipidemia"}],
        ]
        return [{"label": "DIAGNOSTICO", "pattern": p} for p in diagnoses]

    def _build_measurement_patterns(self) -> list[dict[str, Any]]:
        """Construye patrones para mediciones y valores."""
        patterns = []
        dose_patterns = [
            [{"SHAPE": "ddd"}, {"LOWER": "mg"}],
            [{"SHAPE": "dd"}, {"LOWER": "mg"}],
            [{"SHAPE": "dddd"}, {"LOWER": "mg"}],
            [{"SHAPE": "ddd"}, {"LOWER": "ml"}],
            [{"TEXT": {"REGEX": r"^\d+mg$"}}],
            [{"TEXT": {"REGEX": r"^\d+ml$"}}],
        ]
        for p in dose_patterns:
            patterns.append({"label": "DOSIS", "pattern": p})

        vital_patterns = [
            [{"LOWER": "glucosa"}],
            [{"LOWER": "hemoglobina"}],
            [{"LOWER": "colesterol"}],
            [{"LOWER": "trigliceridos"}],
            [{"LOWER": "creatinina"}],
            [{"LOWER": "urea"}],
            [{"LOWER": {"IN": ["presion", "tension"]}}, {"LOWER": "arterial"}],
        ]
        for p in vital_patterns:
            patterns.append({"label": "SIGNO_VITAL", "pattern": p})

        return patterns

    def _build_date_patterns(self) -> list[dict[str, Any]]:
        """Construye patrones para fechas."""
        return [
            {"label": "FECHA", "pattern": [
                {"SHAPE": "dd"}, {"TEXT": "/"}, {"SHAPE": "dd"}, {"TEXT": "/"}, {"SHAPE": "dddd"}
            ]},
            {"label": "FECHA", "pattern": [
                {"SHAPE": "d"}, {"TEXT": "/"}, {"SHAPE": "dd"}, {"TEXT": "/"}, {"SHAPE": "dddd"}
            ]},
        ]

    def extract_entities(self, text: str) -> list[MedicalEntity]:
        """Extrae entidades medicas del texto.

        Combina el NER de SpaCy con reglas regex adicionales
        para maximizar la cobertura de entidades medicas.

        Args:
            text: Texto del documento medico.

        Returns:
            Lista de MedicalEntity con tipo, valor, confianza y posicion.
        """
        if not text or not text.strip():
            return []

        doc = self.nlp(text)
        entities: list[MedicalEntity] = []

        for ent in doc.ents:
            label = ent.label_
            if label in MEDICAL_NER_LABELS or self._is_custom:
                entities.append(MedicalEntity(
                    entity_type=label,
                    value=ent.text,
                    confidence=1.0 if self._is_custom else 0.8,
                    start_char=ent.start_char,
                    end_char=ent.end_char,
                ))

        regex_entities = self._extract_with_regex(text)
        entities = self._merge_entities(entities, regex_entities)

        return entities

    def extract_structured_data(self, text: str, doc_type: str) -> ExtractionResult:
        """Extrae datos estructurados segun tipo de documento.

        Args:
            text: Texto del documento medico.
            doc_type: Tipo de documento (receta, laboratorio, nota_medica, referencia).

        Returns:
            ExtractionResult con entidades y datos estructurados.
        """
        start_time = time.perf_counter()

        entities = self.extract_entities(text)

        extractors = {
            "receta": self._extract_receta,
            "laboratorio": self._extract_laboratorio,
            "nota_medica": self._extract_nota_medica,
            "referencia": self._extract_referencia,
        }

        extractor = extractors.get(doc_type, self._extract_generic)
        structured = extractor(text, entities)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        model_name = self.model_path or "es_core_news_lg+rules"

        return ExtractionResult(
            entities=entities,
            structured_data=structured,
            processing_time_ms=elapsed_ms,
            model_used=model_name,
        )

    def _extract_with_regex(self, text: str) -> list[MedicalEntity]:
        """Extrae entidades adicionales con regex."""
        entities: list[MedicalEntity] = []

        # CIE-10 codes
        for match in re.finditer(r"\b([A-Z]\d{2}(?:\.\d{1,2})?)\b", text):
            entities.append(MedicalEntity(
                entity_type="CODIGO_CIE10",
                value=match.group(1),
                confidence=0.9,
                start_char=match.start(),
                end_char=match.end(),
            ))

        # Dosis patterns like "850mg", "500 mg", "10 ml"
        for match in re.finditer(r"\b(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg|UI)\b", text, re.IGNORECASE):
            entities.append(MedicalEntity(
                entity_type="DOSIS",
                value=match.group(0),
                confidence=0.85,
                start_char=match.start(),
                end_char=match.end(),
            ))

        # Measurement values with units like "126 mg/dL", "140/90 mmHg"
        for match in re.finditer(
            r"\b(\d+(?:\.\d+)?(?:/\d+)?)\s*(mg/dL|g/dL|mmHg|mEq/L|U/L|%|lpm|rpm)\b",
            text, re.IGNORECASE
        ):
            entities.append(MedicalEntity(
                entity_type="VALOR_MEDICION",
                value=match.group(0),
                confidence=0.9,
                start_char=match.start(),
                end_char=match.end(),
            ))

        # Reference ranges like "(70-100 mg/dL)"
        for match in re.finditer(
            r"\((\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?)\s*(mg/dL|g/dL|%|U/L|mEq/L)?\)",
            text
        ):
            entities.append(MedicalEntity(
                entity_type="RANGO_REFERENCIA",
                value=match.group(0),
                confidence=0.85,
                start_char=match.start(),
                end_char=match.end(),
            ))

        # Dates dd/mm/yyyy
        for match in re.finditer(r"\b(\d{1,2}/\d{2}/\d{4})\b", text):
            entities.append(MedicalEntity(
                entity_type="FECHA",
                value=match.group(1),
                confidence=0.9,
                start_char=match.start(),
                end_char=match.end(),
            ))

        # Frequency patterns like "cada 8 horas", "cada 12 horas"
        for match in re.finditer(r"cada\s+(\d+)\s+(horas?|hrs?|dias?|semanas?)", text, re.IGNORECASE):
            entities.append(MedicalEntity(
                entity_type="FRECUENCIA_TIEMPO",
                value=match.group(0),
                confidence=0.85,
                start_char=match.start(),
                end_char=match.end(),
            ))

        # Duration patterns like "por 30 dias", "durante 2 semanas"
        for match in re.finditer(
            r"(?:por|durante)\s+(\d+)\s+(dias?|semanas?|meses?)",
            text, re.IGNORECASE
        ):
            entities.append(MedicalEntity(
                entity_type="DURACION",
                value=match.group(0),
                confidence=0.85,
                start_char=match.start(),
                end_char=match.end(),
            ))

        # Presentation forms
        for match in re.finditer(
            r"\b(tabletas?|capsulas?|jarabe|solucion\s+(?:inyectable|oral)|"
            r"suspension|ampolletas?|gotas|crema|unguento)\b",
            text, re.IGNORECASE
        ):
            entities.append(MedicalEntity(
                entity_type="PRESENTACION",
                value=match.group(0),
                confidence=0.8,
                start_char=match.start(),
                end_char=match.end(),
            ))

        return entities

    def _merge_entities(
        self,
        spacy_entities: list[MedicalEntity],
        regex_entities: list[MedicalEntity],
    ) -> list[MedicalEntity]:
        """Combina entidades de SpaCy y regex, eliminando duplicados."""
        merged: list[MedicalEntity] = list(spacy_entities)

        for regex_ent in regex_entities:
            is_duplicate = False
            for existing in merged:
                if (
                    abs(regex_ent.start_char - existing.start_char) < 3
                    and abs(regex_ent.end_char - existing.end_char) < 3
                ):
                    is_duplicate = True
                    if regex_ent.confidence > existing.confidence:
                        existing.entity_type = regex_ent.entity_type
                        existing.confidence = regex_ent.confidence
                    break
            if not is_duplicate:
                merged.append(regex_ent)

        merged.sort(key=lambda e: e.start_char)
        return merged

    def _extract_receta(self, text: str, entities: list[MedicalEntity]) -> dict[str, Any]:
        """Extrae datos estructurados de una receta medica."""
        medications: list[dict[str, Any]] = []
        med_entities = [e for e in entities if e.entity_type == "MEDICAMENTO"]

        for med in med_entities:
            med_data: dict[str, Any] = {"nombre": med.value}

            nearby = [
                e for e in entities
                if e.start_char >= med.start_char - 10
                and e.start_char <= med.end_char + 200
                and e.entity_type != "MEDICAMENTO"
            ]

            for ent in nearby:
                if ent.entity_type == "DOSIS" and "dosis" not in med_data:
                    med_data["dosis"] = ent.value
                elif ent.entity_type == "PRESENTACION" and "presentacion" not in med_data:
                    med_data["presentacion"] = ent.value
                elif ent.entity_type == "FRECUENCIA_TIEMPO" and "frecuencia" not in med_data:
                    med_data["frecuencia"] = ent.value
                elif ent.entity_type == "DURACION" and "duracion" not in med_data:
                    med_data["duracion"] = ent.value

            medications.append(med_data)

        diagnosticos = [e.value for e in entities if e.entity_type == "DIAGNOSTICO"]
        codigos = [e.value for e in entities if e.entity_type == "CODIGO_CIE10"]
        fechas = [e.value for e in entities if e.entity_type == "FECHA"]

        return {
            "medicamentos": medications,
            "diagnostico": diagnosticos[0] if diagnosticos else None,
            "codigo_cie10": codigos[0] if codigos else None,
            "fecha": fechas[0] if fechas else None,
        }

    def _extract_laboratorio(self, text: str, entities: list[MedicalEntity]) -> dict[str, Any]:
        """Extrae datos estructurados de resultados de laboratorio."""
        resultados: list[dict[str, Any]] = []
        vital_entities = [e for e in entities if e.entity_type == "SIGNO_VITAL"]

        for vital in vital_entities:
            result: dict[str, Any] = {"analisis": vital.value}

            nearby_values = [
                e for e in entities
                if e.entity_type == "VALOR_MEDICION"
                and e.start_char >= vital.start_char
                and e.start_char <= vital.end_char + 100
            ]
            if nearby_values:
                result["valor"] = nearby_values[0].value

            nearby_ranges = [
                e for e in entities
                if e.entity_type == "RANGO_REFERENCIA"
                and e.start_char >= vital.start_char
                and e.start_char <= vital.end_char + 150
            ]
            if nearby_ranges:
                result["rango_referencia"] = nearby_ranges[0].value

            resultados.append(result)

        fechas = [e.value for e in entities if e.entity_type == "FECHA"]
        return {
            "resultados": resultados,
            "fecha": fechas[0] if fechas else None,
        }

    def _extract_nota_medica(self, text: str, entities: list[MedicalEntity]) -> dict[str, Any]:
        """Extrae datos estructurados de una nota medica."""
        diagnosticos = [e.value for e in entities if e.entity_type == "DIAGNOSTICO"]
        codigos = [e.value for e in entities if e.entity_type == "CODIGO_CIE10"]
        vitales = [
            {"tipo": e.value}
            for e in entities if e.entity_type == "SIGNO_VITAL"
        ]
        medicamentos = [e.value for e in entities if e.entity_type == "MEDICAMENTO"]
        fechas = [e.value for e in entities if e.entity_type == "FECHA"]

        return {
            "diagnostico": diagnosticos,
            "codigos_cie10": codigos,
            "signos_vitales": vitales,
            "medicamentos_mencionados": medicamentos,
            "fecha": fechas[0] if fechas else None,
        }

    def _extract_referencia(self, text: str, entities: list[MedicalEntity]) -> dict[str, Any]:
        """Extrae datos estructurados de una referencia/contrareferencia."""
        diagnosticos = [e.value for e in entities if e.entity_type == "DIAGNOSTICO"]
        medicamentos = [e.value for e in entities if e.entity_type == "MEDICAMENTO"]
        fechas = [e.value for e in entities if e.entity_type == "FECHA"]

        return {
            "diagnostico": diagnosticos[0] if diagnosticos else None,
            "medicamentos_previos": medicamentos,
            "fecha": fechas[0] if fechas else None,
        }

    def _extract_generic(self, text: str, entities: list[MedicalEntity]) -> dict[str, Any]:
        """Extraccion generica para documentos no clasificados."""
        grouped: dict[str, list[str]] = {}
        for ent in entities:
            grouped.setdefault(ent.entity_type, []).append(ent.value)
        return grouped

    @staticmethod
    def train_custom_model(
        training_data_path: str,
        output_path: str,
        base_model: str = "es_core_news_lg",
        n_iter: int = 30,
        dropout: float = 0.3,
        batch_size: int = 16,
    ) -> dict[str, Any]:
        """Entrena modelo NER custom con datos anotados.

        Pasos:
        1. Cargar datos de entrenamiento (formato JSON con anotaciones)
        2. Crear pipeline NER sobre modelo base
        3. Agregar labels custom
        4. Entrenar con mini-batches y dropout
        5. Evaluar en set de validacion
        6. Guardar mejor modelo

        Args:
            training_data_path: Ruta al archivo JSON de entrenamiento.
            output_path: Ruta para guardar el modelo entrenado.
            base_model: Modelo SpaCy base para fine-tuning.
            n_iter: Numero de iteraciones de entrenamiento.
            dropout: Tasa de dropout.
            batch_size: Tamano de mini-batch.

        Returns:
            Diccionario con metricas de entrenamiento.
        """
        from spacy.training import Example
        from spacy.util import minibatch
        import random

        logger.info(
            "training_ner_model",
            data_path=training_data_path,
            base_model=base_model,
            n_iter=n_iter,
        )

        with open(training_data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        training_data = []
        for item in raw_data:
            text = item["text"]
            entities_raw = item.get("entities", [])
            entities_formatted = [(e[0], e[1], e[2]) for e in entities_raw]
            training_data.append((text, {"entities": entities_formatted}))

        random.shuffle(training_data)
        split_idx = int(len(training_data) * 0.8)
        train_data = training_data[:split_idx]
        eval_data = training_data[split_idx:]

        try:
            nlp = spacy.load(base_model)
        except OSError:
            nlp = spacy.blank("es")

        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner")
        else:
            ner = nlp.get_pipe("ner")

        for label in MEDICAL_NER_LABELS:
            ner.add_label(label)

        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        losses_history: list[dict[str, float]] = []
        best_f1 = 0.0

        with nlp.disable_pipes(*other_pipes):
            optimizer = nlp.begin_training()

            for iteration in range(n_iter):
                random.shuffle(train_data)
                losses: dict[str, float] = {}

                batches = minibatch(train_data, size=batch_size)
                for batch in batches:
                    examples = []
                    for text, annotations in batch:
                        doc = nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        examples.append(example)
                    nlp.update(examples, drop=dropout, sgd=optimizer, losses=losses)

                losses_history.append(losses)

                if (iteration + 1) % 5 == 0:
                    eval_scores = _evaluate_ner(nlp, eval_data)
                    f1 = eval_scores.get("f1", 0.0)
                    logger.info(
                        "training_progress",
                        iteration=iteration + 1,
                        loss=losses.get("ner", 0.0),
                        eval_f1=f1,
                    )
                    if f1 > best_f1:
                        best_f1 = f1
                        nlp.to_disk(output_path)

        if best_f1 == 0.0:
            nlp.to_disk(output_path)

        final_scores = _evaluate_ner(nlp, eval_data)

        return {
            "iterations": n_iter,
            "training_samples": len(train_data),
            "eval_samples": len(eval_data),
            "final_loss": losses_history[-1] if losses_history else {},
            "eval_scores": final_scores,
            "best_f1": best_f1,
            "model_path": output_path,
        }


def _evaluate_ner(nlp: Language, eval_data: list[tuple[str, dict]]) -> dict[str, float]:
    """Evalua modelo NER en datos de validacion.

    Args:
        nlp: Modelo SpaCy a evaluar.
        eval_data: Lista de tuplas (text, annotations).

    Returns:
        Diccionario con precision, recall y f1.
    """
    from spacy.training import Example

    examples = []
    for text, annotations in eval_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        examples.append(example)

    if not examples:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    scorer = nlp.evaluate(examples)
    ents_score = scorer.get("ents_f", 0.0)
    ents_p = scorer.get("ents_p", 0.0)
    ents_r = scorer.get("ents_r", 0.0)

    return {
        "precision": ents_p,
        "recall": ents_r,
        "f1": ents_score,
    }
