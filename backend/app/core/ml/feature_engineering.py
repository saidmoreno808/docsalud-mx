"""
Extraccion de features de documentos procesados para modelos ML.

Transforma texto crudo y datos estructurados de pacientes en
vectores de features numericos para clasificacion y clustering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy.sparse import issparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.utils.logger import get_logger

logger = get_logger(__name__)

MEDICAL_KEYWORDS: list[str] = [
    "diabetes", "hipertension", "glucosa", "insulina", "metformina",
    "losartan", "colesterol", "trigliceridos", "hemoglobina", "creatinina",
    "receta", "laboratorio", "diagnostico", "tratamiento", "medicamento",
    "tableta", "capsula", "dosis", "mg", "ml", "via oral",
    "cada 8 horas", "cada 12 horas", "cada 24 horas",
    "referencia", "contrareferencia", "nota medica",
    "presion arterial", "frecuencia cardiaca", "temperatura",
]


@dataclass
class FeatureSet:
    """Conjunto de features extraidas."""

    features: np.ndarray
    feature_names: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class FeatureEngineer:
    """Pipeline de feature engineering para documentos medicos."""

    def __init__(
        self,
        max_tfidf_features: int = 5000,
        ngram_range: tuple[int, int] = (1, 2),
    ) -> None:
        """Inicializa el FeatureEngineer.

        Args:
            max_tfidf_features: Numero maximo de features TF-IDF.
            ngram_range: Rango de n-gramas para TF-IDF.
        """
        self.max_tfidf_features = max_tfidf_features
        self.ngram_range = ngram_range
        self._tfidf: Optional[TfidfVectorizer] = None
        self._scaler: Optional[StandardScaler] = None
        self._label_encoder: Optional[LabelEncoder] = None
        self._is_fitted = False

    @property
    def tfidf(self) -> TfidfVectorizer:
        """Lazy init de TF-IDF vectorizer."""
        if self._tfidf is None:
            self._tfidf = TfidfVectorizer(
                max_features=self.max_tfidf_features,
                ngram_range=self.ngram_range,
                strip_accents="unicode",
                lowercase=True,
                sublinear_tf=True,
            )
        return self._tfidf

    @property
    def scaler(self) -> StandardScaler:
        """Lazy init de StandardScaler."""
        if self._scaler is None:
            self._scaler = StandardScaler()
        return self._scaler

    def fit_text_features(self, texts: list[str]) -> None:
        """Ajusta el vectorizador TF-IDF con un corpus de textos.

        Args:
            texts: Lista de textos de entrenamiento.
        """
        self.tfidf.fit(texts)
        self._is_fitted = True
        logger.info(
            "tfidf_fitted",
            n_documents=len(texts),
            n_features=len(self.tfidf.vocabulary_),
        )

    def extract_text_features(self, text: str) -> np.ndarray:
        """Extrae features basadas en texto de un documento.

        Features incluyen:
        - TF-IDF (si el vectorizador fue ajustado)
        - Longitud del texto
        - Numero de oraciones
        - Ratio de numeros vs texto
        - Presencia de keywords medicos
        - Numero de lineas

        Args:
            text: Texto del documento.

        Returns:
            Vector de features como numpy array.
        """
        manual_features = self._extract_manual_text_features(text)

        if self._is_fitted:
            tfidf_vector = self.tfidf.transform([text])
            if issparse(tfidf_vector):
                tfidf_array = tfidf_vector.toarray().flatten()
            else:
                tfidf_array = np.asarray(tfidf_vector).flatten()
            return np.concatenate([tfidf_array, manual_features])

        return manual_features

    def extract_text_features_batch(self, texts: list[str]) -> np.ndarray:
        """Extrae features de texto para un lote de documentos.

        Si TF-IDF no esta ajustado, lo ajusta con los textos dados.

        Args:
            texts: Lista de textos.

        Returns:
            Matriz de features (n_samples, n_features).
        """
        if not self._is_fitted:
            self.fit_text_features(texts)

        tfidf_matrix = self.tfidf.transform(texts)
        if issparse(tfidf_matrix):
            tfidf_array = tfidf_matrix.toarray()
        else:
            tfidf_array = np.asarray(tfidf_matrix)

        manual = np.array([self._extract_manual_text_features(t) for t in texts])
        return np.hstack([tfidf_array, manual])

    def extract_patient_features(self, patient_data: dict[str, Any]) -> np.ndarray:
        """Extrae features del paciente para clustering de riesgo.

        Features:
        - Edad
        - Genero (codificado)
        - Numero de condiciones cronicas
        - Numero de medicamentos activos
        - Frecuencia de visitas (ultimos 6 meses)
        - Valores de laboratorio recientes (normalizados)
        - Numero de alertas previas
        - Tiempo desde ultima consulta (dias)

        Args:
            patient_data: Diccionario con datos del paciente.

        Returns:
            Vector de features del paciente.
        """
        features: list[float] = []

        features.append(float(patient_data.get("age", 0)))

        gender = patient_data.get("gender", "unknown")
        gender_map = {"M": 0.0, "F": 1.0, "male": 0.0, "female": 1.0}
        features.append(gender_map.get(gender, 0.5))

        chronic = patient_data.get("chronic_conditions", [])
        features.append(float(len(chronic) if isinstance(chronic, list) else 0))

        medications = patient_data.get("active_medications", [])
        features.append(float(len(medications) if isinstance(medications, list) else 0))

        features.append(float(patient_data.get("visit_frequency_6m", 0)))

        lab_values = patient_data.get("recent_lab_values", {})
        features.append(float(lab_values.get("glucosa", 0.0)))
        features.append(float(lab_values.get("hemoglobina", 0.0)))
        features.append(float(lab_values.get("colesterol", 0.0)))
        features.append(float(lab_values.get("trigliceridos", 0.0)))
        features.append(float(lab_values.get("creatinina", 0.0)))
        features.append(float(lab_values.get("presion_sistolica", 0.0)))
        features.append(float(lab_values.get("presion_diastolica", 0.0)))

        features.append(float(patient_data.get("alert_count", 0)))
        features.append(float(patient_data.get("days_since_last_visit", 0)))

        return np.array(features, dtype=np.float64)

    def extract_patient_features_batch(
        self, patients: list[dict[str, Any]]
    ) -> tuple[np.ndarray, list[str]]:
        """Extrae features de multiples pacientes.

        Args:
            patients: Lista de diccionarios de datos de pacientes.

        Returns:
            Tupla (matriz de features, lista de nombres de features).
        """
        feature_names = [
            "age", "gender", "n_chronic_conditions", "n_active_medications",
            "visit_frequency_6m", "glucosa", "hemoglobina", "colesterol",
            "trigliceridos", "creatinina", "presion_sistolica",
            "presion_diastolica", "alert_count", "days_since_last_visit",
        ]

        features = np.array([self.extract_patient_features(p) for p in patients])
        return features, feature_names

    def extract_lab_features(self, lab_results: list[dict[str, Any]]) -> np.ndarray:
        """Extrae features de resultados de laboratorio.

        Features por resultado:
        - Valor normalizado
        - Distancia al rango normal (0 si dentro del rango)
        - Flag fuera de rango (0 o 1)

        Args:
            lab_results: Lista de resultados de laboratorio.
                Cada dict debe tener: value, range_min, range_max.

        Returns:
            Vector de features de laboratorio.
        """
        if not lab_results:
            return np.zeros(3, dtype=np.float64)

        features: list[float] = []
        out_of_range_count = 0

        for result in lab_results:
            value = float(result.get("value", 0))
            range_min = float(result.get("range_min", 0))
            range_max = float(result.get("range_max", 1))

            range_span = range_max - range_min
            if range_span > 0:
                normalized = (value - range_min) / range_span
            else:
                normalized = 0.0

            if value < range_min:
                distance = (range_min - value) / max(range_span, 1)
                out_of_range_count += 1
            elif value > range_max:
                distance = (value - range_max) / max(range_span, 1)
                out_of_range_count += 1
            else:
                distance = 0.0

            features.extend([normalized, distance])

        features.append(float(out_of_range_count))
        features.append(float(out_of_range_count / max(len(lab_results), 1)))

        return np.array(features, dtype=np.float64)

    def normalize_features(
        self, features: np.ndarray, fit: bool = False
    ) -> np.ndarray:
        """Normaliza features usando StandardScaler.

        Args:
            features: Matriz de features.
            fit: Si True, ajusta el scaler con estos datos.

        Returns:
            Features normalizadas.
        """
        if fit:
            return self.scaler.fit_transform(features)
        return self.scaler.transform(features)

    def _extract_manual_text_features(self, text: str) -> np.ndarray:
        """Extrae features manuales de un texto."""
        if not text:
            return np.zeros(6 + len(MEDICAL_KEYWORDS), dtype=np.float64)

        text_lower = text.lower()

        length = len(text)
        n_lines = text.count("\n") + 1
        n_words = len(text.split())

        sentences = [s for s in re.split(r"[.!?\n]+", text) if s.strip()]
        n_sentences = len(sentences)

        digits = sum(c.isdigit() for c in text)
        alpha = sum(c.isalpha() for c in text)
        digit_ratio = digits / max(alpha + digits, 1)

        avg_word_len = np.mean([len(w) for w in text.split()]) if n_words > 0 else 0.0

        base_features = [
            float(length),
            float(n_lines),
            float(n_words),
            float(n_sentences),
            float(digit_ratio),
            float(avg_word_len),
        ]

        keyword_features = [
            1.0 if kw in text_lower else 0.0 for kw in MEDICAL_KEYWORDS
        ]

        return np.array(base_features + keyword_features, dtype=np.float64)
