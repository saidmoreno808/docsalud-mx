"""
Motor de diagnostico predictivo powered by DO Gradient AI.

Orquesta: ML risk scoring + lab anomaly detection + RAG context
+ DO Gradient AI LLM para generar recomendaciones clinicas en espanol.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import structlog

from app.core.diagnosis.prompts import MEDICAL_TRIAGE_SYSTEM_PROMPT
from app.core.gradient.do_gradient_client import DOGradientClient
from app.core.ml.anomaly_detector import LabAnomalyDetector
from app.core.ml.risk_clusterer import RiskClusterer
from app.core.rag.vector_store import VectorStore

logger = structlog.get_logger()


@dataclass
class DiagnosticResult:
    """Resultado completo del diagnostico predictivo."""

    risk_score: float
    risk_level: str
    anomalies: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    referred_to: str | None = None
    suggested_studies: list[str] = field(default_factory=list)
    confidence: float = 0.75
    sources_used: list[str] = field(default_factory=list)
    gradient_model_used: str = ""


class PredictiveDiagnosticEngine:
    """Motor de diagnostico preventivo powered by DO Gradient AI."""

    def __init__(
        self,
        gradient_client: DOGradientClient,
        risk_clusterer: RiskClusterer,
        anomaly_detector: LabAnomalyDetector,
        vector_store: VectorStore,
    ) -> None:
        self.gradient = gradient_client
        self.risk_clusterer = risk_clusterer
        self.anomaly_detector = anomaly_detector
        self.vector_store = vector_store

    async def diagnose(self, patient_data: dict) -> DiagnosticResult:
        """
        Ejecuta diagnostico predictivo completo usando DO Gradient AI.

        Args:
            patient_data: {
                patient_id, age, gender, diagnoses: [],
                medications: [], lab_values: {}, last_visit: str
            }

        Returns:
            DiagnosticResult con risk score, nivel, anomalias y recomendaciones.
        """
        # 1. Risk score con modelo ML existente (RiskClusterer)
        risk_score = self._compute_risk_score(patient_data)

        # 2. Deteccion de anomalias en labs con Autoencoder existente
        anomalies = self._detect_lab_anomalies(patient_data.get("lab_values", {}))

        # 3. RAG: buscar expedientes similares en pgvector
        similar_cases = await self._retrieve_similar_cases(patient_data)

        # 4. Construir contexto para DO Gradient AI
        context = self._build_context(patient_data, anomalies, similar_cases)

        # 5. Llamar DO Gradient AI para analisis clinico
        gradient_response = await self.gradient.complete(
            messages=[{"role": "user", "content": context}],
            system=MEDICAL_TRIAGE_SYSTEM_PROMPT,
            max_tokens=1000,
        )
        logger.info(
            "gradient_diagnosis_complete",
            patient_id=patient_data.get("patient_id"),
            risk_score=risk_score,
        )

        # 6. Parsear respuesta JSON del LLM
        parsed = self._parse_gradient_response(gradient_response)

        return DiagnosticResult(
            risk_score=risk_score,
            risk_level=parsed.get("nivel_riesgo", self._score_to_level(risk_score)),
            anomalies=anomalies + parsed.get("hallazgos_criticos", []),
            recommendations=parsed.get("recomendaciones", []),
            referred_to=parsed.get("derivacion"),
            suggested_studies=parsed.get("estudios_sugeridos", []),
            confidence=float(parsed.get("confianza", 0.75)),
            sources_used=[c["id"] for c in similar_cases if "id" in c],
            gradient_model_used=self.gradient.model,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_risk_score(self, patient_data: dict) -> float:
        """
        Usa RiskClusterer ML existente para score 0-100.

        Cae al fallback basado en edad y diagnosticos si el modelo no esta entrenado.
        """
        try:
            features = self.risk_clusterer.extract_features(patient_data)
            cluster = self.risk_clusterer.predict_cluster(features)
            return float(self.risk_clusterer.cluster_to_risk_score(cluster))
        except Exception:
            age = patient_data.get("age", 40)
            n_diagnoses = len(patient_data.get("diagnoses", []))
            return min(100.0, age * 0.5 + n_diagnoses * 10)

    def _detect_lab_anomalies(self, lab_values: dict) -> list[str]:
        """Usa LabAnomalyDetector existente, con fallback a lista vacia."""
        if not lab_values:
            return []
        try:
            return self.anomaly_detector.detect(lab_values)
        except Exception:
            return []

    async def _retrieve_similar_cases(self, patient_data: dict) -> list[dict]:
        """RAG: busca expedientes similares en pgvector."""
        diagnoses = patient_data.get("diagnoses", [])
        query = (
            f"paciente {patient_data.get('age')} años, "
            f"diagnósticos: {', '.join(diagnoses)}"
        )
        try:
            results = await self.vector_store.similarity_search(query, k=3)
            return results[:3]
        except Exception:
            return []

    def _build_context(
        self, patient_data: dict, anomalies: list[str], similar_cases: list[dict]
    ) -> str:
        """Construye el prompt de contexto para DO Gradient AI."""
        context = f"""
DATOS DEL PACIENTE:
- Edad: {patient_data.get('age')} años
- Género: {patient_data.get('gender')}
- Diagnósticos previos: {', '.join(patient_data.get('diagnoses', ['Ninguno']))}
- Medicamentos actuales: {', '.join(patient_data.get('medications', ['Ninguno']))}
- Valores de laboratorio: {json.dumps(patient_data.get('lab_values', {}), ensure_ascii=False)}
- Anomalías detectadas por ML: {', '.join(anomalies) if anomalies else 'Ninguna'}

CASOS SIMILARES EN BASE DE DATOS ({len(similar_cases)} encontrados):
{chr(10).join([f"- {c.get('summary', '')}" for c in similar_cases]) if similar_cases else 'Sin casos similares disponibles'}

Analiza este paciente y proporciona tu evaluación clínica en el formato JSON indicado.
"""
        return context

    def _parse_gradient_response(self, response: str) -> dict:
        """Parsea la respuesta JSON de DO Gradient AI."""
        try:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {}

    def _score_to_level(self, score: float) -> str:
        """Convierte score numerico a nivel de riesgo."""
        if score < 25:
            return "BAJO"
        if score < 50:
            return "MODERADO"
        if score < 75:
            return "ALTO"
        return "CRÍTICO"
