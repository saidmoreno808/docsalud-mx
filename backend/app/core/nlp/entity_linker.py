"""
Vinculacion de entidades medicas a catalogos de referencia.

Vincula entidades extraidas (medicamentos, diagnosticos) a
codigos estandar como CIE-10 y cuadro basico de medicamentos.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from app.core.nlp.ner_extractor import MedicalEntity
from app.utils.logger import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "reference"


class EntityLinker:
    """Vincula entidades medicas a catalogos de referencia."""

    def __init__(
        self,
        cie10_path: Optional[str] = None,
        medications_path: Optional[str] = None,
        lab_ranges_path: Optional[str] = None,
    ) -> None:
        """Inicializa el EntityLinker cargando catalogos.

        Args:
            cie10_path: Ruta al JSON de codigos CIE-10.
            medications_path: Ruta al JSON de medicamentos.
            lab_ranges_path: Ruta al JSON de rangos de laboratorio.
        """
        self._cie10: list[dict[str, Any]] = self._load_json(
            cie10_path or str(DATA_DIR / "cie10_codes.json")
        )
        self._medications: list[dict[str, Any]] = self._load_json(
            medications_path or str(DATA_DIR / "medications.json")
        )
        self._lab_ranges: list[dict[str, Any]] = self._load_json(
            lab_ranges_path or str(DATA_DIR / "lab_ranges.json")
        )

        self._cie10_index: dict[str, dict[str, Any]] = {}
        for item in self._cie10:
            code = item.get("code", "")
            self._cie10_index[code] = item
            name = item.get("name", "").lower()
            self._cie10_index[name] = item

        self._med_index: dict[str, dict[str, Any]] = {}
        for item in self._medications:
            name = item.get("generic_name", "").lower()
            self._med_index[name] = item

        self._lab_index: dict[str, dict[str, Any]] = {}
        for item in self._lab_ranges:
            name = item.get("name", "").lower()
            self._lab_index[name] = item

    def link_entities(self, entities: list[MedicalEntity]) -> list[dict[str, Any]]:
        """Vincula una lista de entidades a catalogos de referencia.

        Args:
            entities: Lista de entidades extraidas por NER.

        Returns:
            Lista de diccionarios con entidad original + datos de referencia.
        """
        linked: list[dict[str, Any]] = []

        for entity in entities:
            link_data: dict[str, Any] = {
                "entity_type": entity.entity_type,
                "value": entity.value,
                "start_char": entity.start_char,
                "end_char": entity.end_char,
                "confidence": entity.confidence,
                "reference": None,
            }

            if entity.entity_type == "MEDICAMENTO":
                ref = self._link_medication(entity.value)
                if ref:
                    link_data["reference"] = ref
                    entity.normalized_value = ref.get("generic_name")

            elif entity.entity_type == "DIAGNOSTICO":
                ref = self._link_diagnosis(entity.value)
                if ref:
                    link_data["reference"] = ref
                    entity.normalized_value = ref.get("code")

            elif entity.entity_type == "CODIGO_CIE10":
                ref = self._link_cie10_code(entity.value)
                if ref:
                    link_data["reference"] = ref
                    entity.normalized_value = ref.get("name")

            elif entity.entity_type == "SIGNO_VITAL":
                ref = self._link_lab_test(entity.value)
                if ref:
                    link_data["reference"] = ref

            linked.append(link_data)

        return linked

    def _link_medication(self, value: str) -> Optional[dict[str, Any]]:
        """Busca un medicamento en el catalogo."""
        key = value.strip().lower()
        if key in self._med_index:
            return self._med_index[key]

        for name, data in self._med_index.items():
            if key in name or name in key:
                return data

        return None

    def _link_diagnosis(self, value: str) -> Optional[dict[str, Any]]:
        """Busca un diagnostico en el catalogo CIE-10."""
        key = value.strip().lower()
        if key in self._cie10_index:
            return self._cie10_index[key]

        for name, data in self._cie10_index.items():
            if not name[0].isalpha() or name[0].isupper():
                continue
            if key in name or name in key:
                return data

        return None

    def _link_cie10_code(self, value: str) -> Optional[dict[str, Any]]:
        """Busca un codigo CIE-10 directo."""
        return self._cie10_index.get(value)

    def _link_lab_test(self, value: str) -> Optional[dict[str, Any]]:
        """Busca un examen de laboratorio en el catalogo."""
        key = value.strip().lower()
        if key in self._lab_index:
            return self._lab_index[key]

        for name, data in self._lab_index.items():
            if key in name or name in key:
                return data

        return None

    def _load_json(self, path: str) -> list[dict[str, Any]]:
        """Carga archivo JSON de referencia."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("items", data.get("codes", [data]))
            return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning("reference_file_load_error", path=path, error=str(e))
            return []
