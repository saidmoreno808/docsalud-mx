# CLAUDE_HACKATHON.md — ClinicaIA: DO Gradient AI Hackathon Edition

> **Proyecto base:** DocSalud MX (comenzado Feb 14, 2026)
> **Autor:** Said Ivan Briones Moreno
> **Deadline:** March 18, 2026 — 5:00 pm Eastern Time
> **Objetivo:** Adaptar DocSalud MX para el DigitalOcean Gradient AI Hackathon

---

## ⚠️ INSTRUCCIÓN PARA CLAUDE CODE

Lee este archivo COMPLETO antes de ejecutar cualquier tarea.
El proyecto base YA EXISTE en `docsalud-mx/`. NO recrear nada que ya funcione.
Solo agregar, modificar o migrar lo indicado en cada fase.

---

## 🎯 QUÉ ES ESTE PROYECTO

**ClinicaIA** es DocSalud MX adaptado para el hackathon.

El sistema ya digitaliza expedientes médicos con OCR + NLP + ML.
Lo que agregamos: **diagnóstico preventivo con DO Gradient AI** como motor de IA.

**Cambios respecto al CLAUDE.md original:**

| Componente | Antes (DocSalud MX) | Ahora (ClinicaIA Hackathon) |
|------------|---------------------|------------------------------|
| LLM Engine | Groq API | DO Gradient AI SDK |
| Deploy | AWS EC2 | DO App Platform |
| Storage | AWS S3 | DO Spaces (boto3 compatible) |
| Database | Supabase pgvector | DO Managed PostgreSQL + pgvector |
| Nuevo endpoint | — | POST /api/v1/diagnose |
| Nuevo módulo | — | backend/app/core/gradient/ |
| Nuevo frontend | — | DiagnosticPanel con RiskGauge |

---

## 🔑 VARIABLES DE ENTORNO REQUERIDAS

Agrega estas variables a tu `.env` (además de las que ya tienes):

```bash
# DigitalOcean Gradient AI
DO_GRADIENT_API_KEY=tu_model_access_key_aqui
DO_GRADIENT_MODEL=llama3-3-70b-instruct

# DigitalOcean App Platform
DO_API_TOKEN=tu_do_api_token
DO_APP_ID=                        # se llena después del primer deploy

# DigitalOcean Managed Database
DO_DATABASE_URL=                  # se llena después de crear la DB

# DigitalOcean Spaces (reemplaza S3)
DO_SPACES_KEY=
DO_SPACES_SECRET=
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_BUCKET=clinicaia-docs
```

Crea tu Model Access Key en:
https://cloud.digitalocean.com/gen-ai → Serverless Inference → "Create model access key"

---

## 📁 ARCHIVOS NUEVOS A CREAR

```
docsalud-mx/
├── CLAUDE_HACKATHON.md              ← ESTE ARCHIVO
├── .do/
│   └── app.yaml                     ← DO App Platform spec
├── backend/
│   ├── requirements.txt             ← agregar: gradient-ai
│   └── app/
│       ├── config.py                ← agregar vars DO Gradient
│       ├── core/
│       │   └── gradient/            ← NUEVO MÓDULO
│       │       ├── __init__.py
│       │       ├── do_gradient_client.py
│       │       └── gradient_inference_service.py
│       │   └── diagnosis/           ← NUEVO MÓDULO
│       │       ├── __init__.py
│       │       ├── predictive_engine.py
│       │       └── prompts.py
│       └── api/v1/
│           └── endpoints/
│               └── diagnose.py      ← NUEVO ENDPOINT
├── frontend/src/
│   └── components/
│       └── DiagnosticPanel/         ← NUEVO COMPONENTE
│           ├── index.tsx
│           ├── RiskGauge.tsx
│           ├── DiagnosticButton.tsx
│           └── types.ts
└── infrastructure/
    └── scripts/
        └── setup_do_database.sh     ← NUEVO SCRIPT
```

---

## 🚀 PIPELINE DE EJECUCIÓN — 7 FASES

Ejecuta en orden estricto. Cada fase tiene un checkpoint de validación.

---

### FASE 1 — DO Gradient AI Client
**Tiempo estimado:** 2 horas
**Checkpoint:** `pytest backend/tests/unit/test_do_gradient_client.py -v` pasa

**Prompt exacto para Claude Code:**
```
Lee el CLAUDE_HACKATHON.md. Estamos en FASE 1.

Instala la dependencia: agrega "gradient-ai" al backend/requirements.txt

Crea backend/app/core/gradient/do_gradient_client.py con la clase DOGradientClient:

```python
import asyncio
from gradient import Gradient
from app.config import settings
import structlog

logger = structlog.get_logger()

class DOGradientClient:
    """Cliente oficial para DigitalOcean Gradient AI SDK."""
    
    def __init__(self, model_access_key: str | None = None, model: str | None = None):
        self.model_access_key = model_access_key or settings.DO_GRADIENT_API_KEY
        self.model = model or settings.DO_GRADIENT_MODEL
        self._client = None

    @property
    def client(self) -> Gradient:
        if self._client is None:
            self._client = Gradient(model_access_key=self.model_access_key)
        return self._client

    async def complete(self, messages: list[dict], system: str = "", max_tokens: int = 1500) -> str:
        """Chat completion via DO Gradient AI. Compatible con interfaz Groq."""
        loop = asyncio.get_event_loop()
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)
        
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                messages=all_messages,
                model=self.model,
                max_tokens=max_tokens,
            )
        )
        logger.info("gradient_ai_call", model=self.model, tokens=response.usage.total_tokens)
        return response.choices[0].message.content

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embeddings via DO Gradient AI GPU."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002"
            )
        )
        return [d.embedding for d in response.data]

    async def health_check(self) -> dict:
        """Verifica conectividad con DO Gradient AI."""
        try:
            await self.complete([{"role": "user", "content": "ping"}], max_tokens=5)
            return {"gradient_ai": "connected", "model": self.model}
        except Exception as e:
            logger.error("gradient_ai_health_failed", error=str(e))
            return {"gradient_ai": "error", "detail": str(e)}
```

Actualiza backend/app/config.py — agrega estas variables a la clase Settings:
```python
DO_GRADIENT_API_KEY: str = ""
DO_GRADIENT_MODEL: str = "llama3-3-70b-instruct"
DO_API_TOKEN: str = ""
DO_SPACES_ENDPOINT: str = "https://nyc3.digitaloceanspaces.com"
DO_SPACES_BUCKET: str = "clinicaia-docs"
```

Actualiza backend/app/core/rag/rag_chain.py:
- Reemplaza la importación de Groq por DOGradientClient
- El método que llamaba groq.chat.completions ahora llama client.complete()
- La interfaz externa NO cambia (ningún otro módulo se toca)

Actualiza backend/app/api/v1/endpoints/health.py:
- Agrega al response: gradient_ai status usando DOGradientClient().health_check()
- El /health debe retornar: {"status": "ok", "gradient_ai": "connected", ...}

Agrega al Makefile:
gradient-test:
	pytest backend/tests/unit/test_do_gradient_client.py -v

gradient-ping:
	curl -s http://localhost:8000/api/v1/health | python3 -m json.tool

Escribe tests unitarios completos en backend/tests/unit/test_do_gradient_client.py
usando unittest.mock para mockear el Gradient SDK.

Commit semántico: feat(gradient): integrate DO Gradient AI SDK replacing Groq
```

---

### FASE 2 — Motor de Diagnóstico Predictivo
**Tiempo estimado:** 3 horas
**Checkpoint:** `curl -X POST http://localhost:8000/api/v1/diagnose?patient_id=TEST` retorna DiagnosticResult

**Prompt exacto para Claude Code:**
```
Lee el CLAUDE_HACKATHON.md. Estamos en FASE 2.

PASO 2.1 — Crea backend/app/core/diagnosis/prompts.py

```python
MEDICAL_TRIAGE_SYSTEM_PROMPT = """
Eres un asistente de soporte clínico especializado en medicina familiar
para comunidades rurales de México. 

IMPORTANTE: NO eres un diagnóstico definitivo. Eres apoyo al médico.

Tu función es analizar los datos del paciente y:
1. Identificar señales de alerta y valores críticos
2. Calcular nivel de riesgo: BAJO | MODERADO | ALTO | CRÍTICO
3. Sugerir estudios complementarios si hay anomalías
4. Recomendar seguimiento o derivación según el riesgo
5. Basar análisis en el historial del paciente y casos similares

Reglas:
- Responde SIEMPRE en español
- Sé conciso y clínicamente preciso
- Nunca uses términos que alarmen innecesariamente al paciente
- Si hay datos insuficientes, indícalo claramente

Formato de respuesta (JSON):
{
  "nivel_riesgo": "BAJO|MODERADO|ALTO|CRÍTICO",
  "hallazgos_criticos": ["hallazgo 1", "hallazgo 2"],
  "recomendaciones": ["recomendación 1", "recomendación 2"],
  "derivacion": "Especialidad o null si no aplica",
  "estudios_sugeridos": ["estudio 1"],
  "confianza": 0.85
}
"""
```

PASO 2.2 — Crea backend/app/core/diagnosis/predictive_engine.py

```python
from dataclasses import dataclass
from app.core.gradient.do_gradient_client import DOGradientClient
from app.core.ml.risk_clusterer import RiskClusterer
from app.core.ml.lab_anomaly_detector import LabAnomalyDetector
from app.core.rag.vector_store import VectorStore
from app.core.diagnosis.prompts import MEDICAL_TRIAGE_SYSTEM_PROMPT
import json

@dataclass
class DiagnosticResult:
    risk_score: float          # 0-100
    risk_level: str            # BAJO | MODERADO | ALTO | CRÍTICO
    anomalies: list[str]       # valores fuera de rango detectados
    recommendations: list[str] # recomendaciones clínicas ordenadas
    referred_to: str | None    # especialidad sugerida (o None)
    suggested_studies: list[str]
    confidence: float          # 0.0 - 1.0
    sources_used: list[str]    # IDs de expedientes similares usados en RAG
    gradient_model_used: str   # modelo DO Gradient AI usado

class PredictiveDiagnosticEngine:
    """Motor de diagnóstico preventivo powered by DO Gradient AI."""
    
    def __init__(
        self,
        gradient_client: DOGradientClient,
        risk_clusterer: RiskClusterer,
        anomaly_detector: LabAnomalyDetector,
        vector_store: VectorStore,
    ):
        self.gradient = gradient_client
        self.risk_clusterer = risk_clusterer
        self.anomaly_detector = anomaly_detector
        self.vector_store = vector_store

    async def diagnose(self, patient_data: dict) -> DiagnosticResult:
        """
        Ejecuta diagnóstico predictivo completo usando DO Gradient AI.
        
        patient_data: {
            patient_id, age, gender, diagnoses: [], 
            medications: [], lab_values: {}, last_visit: str
        }
        """
        # 1. Risk score con modelo ML existente (RiskClusterer)
        risk_score = self._compute_risk_score(patient_data)
        
        # 2. Detección de anomalías en labs con Autoencoder existente
        anomalies = self._detect_lab_anomalies(patient_data.get("lab_values", {}))
        
        # 3. RAG: buscar expedientes similares en pgvector
        similar_cases = await self._retrieve_similar_cases(patient_data)
        
        # 4. Construir contexto para DO Gradient AI
        context = self._build_context(patient_data, anomalies, similar_cases)
        
        # 5. Llamar DO Gradient AI para análisis clínico
        gradient_response = await self.gradient.complete(
            messages=[{"role": "user", "content": context}],
            system=MEDICAL_TRIAGE_SYSTEM_PROMPT,
            max_tokens=1000
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
            confidence=parsed.get("confianza", 0.75),
            sources_used=[c["id"] for c in similar_cases],
            gradient_model_used=self.gradient.model,
        )

    def _compute_risk_score(self, patient_data: dict) -> float:
        """Usa RiskClusterer ML existente para score 0-100."""
        try:
            features = self.risk_clusterer.extract_features(patient_data)
            cluster = self.risk_clusterer.predict_cluster(features)
            return float(self.risk_clusterer.cluster_to_risk_score(cluster))
        except Exception:
            # Fallback: score basado en edad y diagnósticos
            age = patient_data.get("age", 40)
            n_diagnoses = len(patient_data.get("diagnoses", []))
            return min(100.0, age * 0.5 + n_diagnoses * 10)

    def _detect_lab_anomalies(self, lab_values: dict) -> list[str]:
        """Usa LabAnomalyDetector existente."""
        if not lab_values:
            return []
        try:
            return self.anomaly_detector.detect(lab_values)
        except Exception:
            return []

    async def _retrieve_similar_cases(self, patient_data: dict) -> list[dict]:
        """RAG: busca expedientes similares en pgvector."""
        query = f"paciente {patient_data.get('age')} años, diagnósticos: {', '.join(patient_data.get('diagnoses', []))}"
        try:
            results = await self.vector_store.similarity_search(query, k=3)
            return results[:3]
        except Exception:
            return []

    def _build_context(self, patient_data: dict, anomalies: list, similar_cases: list) -> str:
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
            # Buscar JSON en la respuesta
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {}

    def _score_to_level(self, score: float) -> str:
        if score < 25: return "BAJO"
        if score < 50: return "MODERADO"
        if score < 75: return "ALTO"
        return "CRÍTICO"
```

PASO 2.3 — Crea backend/app/api/v1/endpoints/diagnose.py

El endpoint debe:
- Recibir: patient_id: UUID como query param
- Obtener datos del paciente de PostgreSQL usando el PatientRepository existente
- Construir patient_data dict con: age, gender, diagnoses (de documentos), lab_values, medications
- Llamar PredictiveDiagnosticEngine.diagnose(patient_data)
- Guardar resultado en una tabla diagnostic_results (crear migración Alembic)
- Si risk_level == "CRÍTICO": agregar a background_tasks la creación de una alerta de severidad HIGH
- Retornar DiagnosticResponse (schema Pydantic con todos los campos de DiagnosticResult)

PASO 2.4 — Crear schema Pydantic:
backend/app/api/v1/schemas/diagnostic.py

PASO 2.5 — Registrar router en backend/app/api/v1/router.py

PASO 2.6 — Crear migración Alembic para tabla diagnostic_results:
alembic revision --autogenerate -m "add diagnostic_results table"

PASO 2.7 — Tests de integración:
backend/tests/integration/test_diagnose_endpoint.py
Mockear DOGradientClient para no consumir créditos en CI

Commit: feat(diagnose): add predictive diagnostic engine with DO Gradient AI
```

---

### FASE 3 — Migración a DigitalOcean App Platform
**Tiempo estimado:** 3 horas
**Checkpoint:** `doctl apps list` muestra la app corriendo + URL pública responde

**Prompt exacto para Claude Code:**
```
Lee el CLAUDE_HACKATHON.md. Estamos en FASE 3.

PASO 3.1 — Crea .do/app.yaml (DO App Platform spec):

```yaml
name: clinicaia-docsalud
region: nyc

services:
  - name: backend
    github:
      repo: saidmoreno808/docsalud-mx
      branch: main
      deploy_on_push: true
    dockerfile_path: backend/Dockerfile
    http_port: 8000
    instance_count: 1
    instance_size_slug: professional-xs
    health_check:
      http_path: /api/v1/health
    envs:
      - key: DO_GRADIENT_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: DATABASE_URL
        scope: RUN_TIME
        type: SECRET
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
      - key: GROQ_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: DO_GRADIENT_MODEL
        scope: RUN_TIME
        value: llama3-3-70b-instruct
      - key: ENVIRONMENT
        scope: RUN_TIME
        value: production

  - name: frontend
    github:
      repo: saidmoreno808/docsalud-mx
      branch: main
      deploy_on_push: true
    source_dir: frontend
    build_command: npm ci && npm run build
    output_dir: dist
    routes:
      - path: /

databases:
  - name: docsalud-db
    engine: PG
    version: "16"
    num_nodes: 1
    size: db-s-1vcpu-1gb
```

PASO 3.2 — Actualiza .github/workflows/cd.yml:
Reemplaza el job que hace SSH a EC2 por este job:

```yaml
deploy-do:
  name: Deploy to DigitalOcean App Platform
  runs-on: ubuntu-latest
  needs: [test, build]
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v4
    - name: Install doctl
      uses: digitalocean/action-doctl@v2
      with:
        token: ${{ secrets.DO_API_TOKEN }}
    - name: Deploy to App Platform
      run: |
        doctl apps update ${{ secrets.DO_APP_ID }} --spec .do/app.yaml
        doctl apps create-deployment ${{ secrets.DO_APP_ID }}
```

PASO 3.3 — Actualiza backend/app/config.py para DO Spaces:
```python
# Reemplaza S3_BUCKET por:
DO_SPACES_ENDPOINT: str = "https://nyc3.digitaloceanspaces.com"
DO_SPACES_BUCKET: str = "clinicaia-docs"
```

En cualquier lugar del código que use boto3 con S3, agrega endpoint_url:
```python
s3_client = boto3.client(
    's3',
    endpoint_url=settings.DO_SPACES_ENDPOINT,
    aws_access_key_id=settings.DO_SPACES_KEY,
    aws_secret_access_key=settings.DO_SPACES_SECRET,
)
```
DO Spaces es 100% compatible con S3. El código boto3 existente funciona sin más cambios.

PASO 3.4 — Crea infrastructure/scripts/setup_do_database.sh:
Script que:
1. Crea la DB managed: doctl databases create docsalud-pg --engine pg --version 16
2. Espera a que esté ONLINE
3. Imprime instrucciones para: CREATE EXTENSION IF NOT EXISTS vector;
4. Imprime el connection string para agregar a DO_DATABASE_URL

PASO 3.5 — Agrega al Makefile:
```makefile
do-deploy:
	doctl apps create --spec .do/app.yaml

do-update:
	doctl apps update $(DO_APP_ID) --spec .do/app.yaml

do-deploy-now:
	doctl apps create-deployment $(DO_APP_ID)

do-logs:
	doctl apps logs $(DO_APP_ID) --follow

do-status:
	doctl apps get $(DO_APP_ID)

do-db-setup:
	bash infrastructure/scripts/setup_do_database.sh
```

Commit: feat(deploy): migrate from AWS EC2 to DigitalOcean App Platform
```

---

### FASE 4 — Frontend: DiagnosticPanel
**Tiempo estimado:** 3 horas
**Checkpoint:** La pantalla de paciente muestra el botón y panel de diagnóstico funcional

**Prompt exacto para Claude Code:**
```
Lee el CLAUDE_HACKATHON.md. Estamos en FASE 4.

Crea el componente DiagnosticPanel en frontend/src/components/DiagnosticPanel/

ARCHIVO: types.ts
```typescript
export interface DiagnosticResult {
  risk_score: number;
  risk_level: 'BAJO' | 'MODERADO' | 'ALTO' | 'CRÍTICO';
  anomalies: string[];
  recommendations: string[];
  referred_to: string | null;
  suggested_studies: string[];
  confidence: number;
  sources_used: string[];
  gradient_model_used: string;
}
```

ARCHIVO: RiskGauge.tsx
Componente SVG que muestra un semicírculo (gauche) con:
- Arco de fondo gris
- Arco de color según nivel: verde (<25), amarillo (25-50), naranja (50-75), rojo (>75)
- Número grande en el centro: risk_score
- Texto debajo: risk_level
- Animación de entrada suave
- Dimensiones: 200x120px

ARCHIVO: index.tsx — DiagnosticPanel completo con:
- RiskGauge en la parte superior
- Sección "Hallazgos" con lista de anomalies (iconos de alerta ⚠️ como SVG, no emoji)
- Sección "Recomendaciones" con lista numerada
- Chip de "Derivar a: {referred_to}" si no es null (color rojo si presente)
- Sección "Estudios sugeridos" si hay
- Barra de confianza: ConfidenceBar con porcentaje
- Footer: "Análisis generado por DO Gradient AI · Modelo: {gradient_model_used}"
- Loading state: skeleton loader mientras carga
- Error state: mensaje amigable si falla

ARCHIVO: DiagnosticButton.tsx
Botón que se agrega a PatientDetail.tsx existente:
- Texto: "Analizar con IA"
- Loading: "Consultando DO Gradient AI..."
- On click: llama useDiagnosis(patientId).mutate()
- Posición: junto al header del paciente

Agrega en frontend/src/services/api.ts:
```typescript
export const diagnosePatient = async (patientId: string): Promise<DiagnosticResult> => {
  const { data } = await apiClient.post(`/diagnose?patient_id=${patientId}`);
  return data;
};
```

Agrega frontend/src/hooks/useDiagnosis.ts:
```typescript
import { useMutation } from '@tanstack/react-query';
import { diagnosePatient } from '../services/api';

export const useDiagnosis = (patientId: string) => {
  return useMutation({
    mutationFn: () => diagnosePatient(patientId),
  });
};
```

Actualiza PatientDetail.tsx:
- Importa DiagnosticButton y DiagnosticPanel
- Agrega estado local: const [diagnosticResult, setDiagnosticResult] = useState(null)
- Agrega DiagnosticButton en el header del paciente
- Renderiza DiagnosticPanel debajo del header cuando hay resultado

Commit: feat(ui): add DiagnosticPanel with RiskGauge powered by DO Gradient AI
```

---

### FASE 5 — README Hackathon
**Tiempo estimado:** 45 minutos
**Checkpoint:** README.md actualizado con sección DO Gradient AI visible

**Prompt exacto para Claude Code:**
```
Lee el CLAUDE_HACKATHON.md. Estamos en FASE 5.

Actualiza README.md con estos cambios específicos:

1. TÍTULO: Cambia a:
   # ClinicaIA — Diagnóstico Preventivo con IA para México
   > Basado en DocSalud MX | Powered by DigitalOcean Gradient AI

2. BADGES: Agrega después de los badges existentes:
   [![DO Gradient AI](https://img.shields.io/badge/DO-Gradient%20AI-0080FF?logo=digitalocean&logoColor=white)](https://docs.digitalocean.com/products/gen-ai/)
   [![Deploy: DO App Platform](https://img.shields.io/badge/deploy-DO%20App%20Platform-0080FF?logo=digitalocean)](https://cloud.digitalocean.com/apps)
   
   Elimina el badge "Deploy: AWS EC2"

3. AGREGA nueva sección después de "## Solución":

## DigitalOcean Gradient AI

ClinicaIA usa [DigitalOcean Gradient AI](https://docs.digitalocean.com/products/gen-ai/) como el núcleo de su motor de diagnóstico predictivo:

| Capacidad Gradient AI | Uso en ClinicaIA |
|----------------------|------------------|
| **Serverless LLM Inference** | Motor de diagnóstico clínico (Llama 3.3 70B) analiza el expediente del paciente y genera recomendaciones en español |
| **Model Access Keys** | Autenticación segura sin infraestructura propia de GPU |
| **OpenAI-compatible API** | Integración directa con el pipeline RAG existente |

El flujo de diagnóstico:
```
Expediente del paciente
    ↓ OCR + NLP (módulos existentes)
Datos estructurados
    ↓ Risk Score ML (RiskClusterer)
    ↓ Anomaly Detection (LabAnomalyDetector)  
    ↓ RAG context (pgvector similarity search)
DO Gradient AI (Llama 3.3 70B)
    ↓ Análisis clínico en español
DiagnosticResult → Frontend Dashboard
```

4. ACTUALIZA tabla de Stack: agrega fila:
   | **DO Gradient AI** | Llama 3.3 70B serverless | - | Motor diagnóstico predictivo |

5. AGREGA en Quick Start:
   ### Deploy en DigitalOcean
   ```bash
   doctl auth init --access-token $DO_API_TOKEN
   doctl apps create --spec .do/app.yaml
   ```

6. ACTUALIZA Roadmap:
   - Elimina: [ ] Fine-tuning de NER con anotaciones médicas reales
   - Agrega:
     - [x] Integración DO Gradient AI — motor diagnóstico predictivo
     - [x] Migración a DigitalOcean App Platform
     - [ ] Fine-tuning modelo médico con DO Gradient AI training

Commit: docs(readme): update for DigitalOcean Gradient AI hackathon submission
```

---

### FASE 6 — Video Pitch (3 minutos)
**Tiempo estimado:** 1.5 horas
**Checkpoint:** Video subido a YouTube, URL lista para Devpost

#### Script exacto del video:

**[0:00 — 0:20] HOOK**
> "En México, más de 15,000 clínicas rurales manejan expedientes en papel.
> Un paciente diabético puede morir porque nadie detectó su HbA1c elevada a tiempo.
> ClinicaIA lo detecta antes. Así."

*[Muestra: foto de expediente en papel → sube a la app]*

---

**[0:20 — 0:45] DEMO UPLOAD + OCR**
> "El médico toma una foto del expediente con su teléfono."
> "ClinicaIA lo digitaliza: OCR con OpenCV y Tesseract."
> "SpaCy extrae automáticamente: diagnósticos, medicamentos, valores de laboratorio."

*[Muestra: dashboard con el expediente ya procesado, entidades resaltadas]*

---

**[0:45 — 1:15] DO GRADIENT AI DEMO — EL MOMENTO CLAVE**
> "Aquí está el núcleo: pulsamos 'Analizar con IA'."
> "ClinicaIA llama a DigitalOcean Gradient AI — Llama 3.3 70B."
> "En segundos: Risk Score 78/100. Nivel: ALTO."
> "Hallazgo: HbA1c 9.2% — descontrol glucémico severo."
> "Recomendación: control urgente, ajuste de metformina, derivar a endocrinología."

*[Muestra: DiagnosticPanel con RiskGauge, anomalías, recomendaciones]*
*[Muestra: log/terminal con la llamada real a DO Gradient AI]*

---

**[1:15 — 1:40] RAG + CHAT**
> "El médico pregunta en lenguaje natural: ¿qué pacientes tienen riesgo similar?"
> "El sistema busca en pgvector, recupera contexto, y DO Gradient AI responde."

*[Muestra: ChatInterface con respuesta del LLM citando expedientes]*

---

**[1:40 — 2:00] ARQUITECTURA (rápido)**
> "Stack completo en DigitalOcean:"
> "App Platform — FastAPI + React. DO Managed PostgreSQL + pgvector."
> "DO Gradient AI Serverless — sin infraestructura GPU propia."

*[Muestra: diagrama simple con logos de DO]*

---

**[2:00 — 2:30] IMPACTO**
> "130 millones de mexicanos. 60% sin seguridad social."
> "Este sistema puede triagear 1,000 pacientes al día con un solo médico."
> "Open source, MIT License. Cualquier clínica puede deployarlo."

---

**[2:30 — 3:00] CTA**
> "ClinicaIA — Diagnóstico preventivo con IA para México."
> "Powered by DigitalOcean Gradient AI."
> "[URL del demo] — [URL del repo]"
> "Said Briones, San Luis Potosí, México."

---

### FASE 7 — Submission Devpost
**Tiempo estimado:** 45 minutos
**Checkpoint:** Submission enviada antes del March 18, 2026 5:00 pm ET

#### Campos exactos para Devpost:

**Project name:** ClinicaIA — Diagnóstico Preventivo con IA para México

**Tagline:** Digitalizando la salud rural mexicana con DigitalOcean Gradient AI

**Description (en inglés, 400+ palabras):**
```
ClinicaIA is an AI-powered preventive diagnostic system that transforms paper 
medical records from rural Mexican clinics into actionable clinical intelligence.

THE PROBLEM:
Over 15,000 rural clinics in Mexico manage medical records exclusively on paper. 
60% of Mexico's population lacks social security coverage. Chronic diseases like 
diabetes and hypertension go undetected until it's too late, not because medicine 
is unavailable, but because there is no system to identify patients at risk.

THE SOLUTION:
ClinicaIA uses DigitalOcean Gradient AI as the core of its predictive diagnostic 
engine. The system:

1. DIGITIZES paper records via OCR (OpenCV + Tesseract) from phone photos
2. EXTRACTS clinical entities with NLP (SpaCy medical NER, NLTK, HuggingFace)  
3. CLASSIFIES documents automatically (ML ensemble: Random Forest + SVM)
4. DETECTS lab anomalies (TF/Keras autoencoder)
5. CLUSTERS patients by risk profile (K-Means + DBSCAN)
6. ANALYZES with DO Gradient AI: sends structured patient data + RAG context 
   to Llama 3.3 70B via DigitalOcean Gradient AI Serverless Inference
7. RETURNS: risk score, critical findings, clinical recommendations in Spanish

HOW WE USE DIGITALOCEAN GRADIENT AI:
- DOGradientClient wraps the official Gradient SDK for async inference
- The predictive engine calls DO Gradient AI with a medical triage system prompt
- Patient data + similar cases from pgvector are sent as context
- DO Gradient AI returns structured JSON: risk level, anomalies, recommendations
- The health endpoint confirms gradient_ai: "connected" status

TECH STACK ON DIGITALOCEAN:
- DO App Platform: FastAPI backend + React 18 frontend
- DO Managed PostgreSQL 16 + pgvector extension
- DO Gradient AI: Serverless LLM inference (Llama 3.3 70B)
- DO Spaces: document storage (PDF/images)

IMPACT:
130 million Mexicans. 60% without social security. ClinicaIA can triage 1,000 
patients per day with a single doctor. Open source (MIT). Any clinic can deploy it.
```

**Built with:** Python, FastAPI, React, TypeScript, DigitalOcean Gradient AI, 
PostgreSQL, pgvector, Docker, OpenCV, SpaCy, HuggingFace, TensorFlow, PyTorch

**Try it:** [URL de DO App Platform]

**Source code:** https://github.com/saidmoreno808/docsalud-mx

---

## ✅ CHECKLIST FINAL DE SUBMISSION

Verifica cada item antes de enviar:

- [ ] `curl https://TU-APP.ondigitalocean.app/api/v1/health` → `{"gradient_ai": "connected"}`
- [ ] `POST /api/v1/diagnose?patient_id=DEMO_ID` retorna DiagnosticResult válido
- [ ] Repo GitHub público con **LICENSE (MIT) visible en la sección About**
- [ ] README.md tiene sección "## DigitalOcean Gradient AI"
- [ ] Badge de CI (GitHub Actions) en verde
- [ ] Video de 3 min subido a YouTube (público o unlisted)
- [ ] Descripción en Devpost menciona DO Gradient AI con detalle técnico
- [ ] Datos de demo son sintéticos (NO datos reales de pacientes)
- [ ] `git log --oneline` muestra commits semánticos por fase

---

## 🛠️ COMANDOS DE REFERENCIA

```bash
# Desarrollo local
make dev                    # FastAPI + React con hot-reload

# DO Gradient AI
make gradient-test          # Tests del cliente Gradient AI
make gradient-ping          # Verifica conexión a DO Gradient AI

# Deploy DigitalOcean
make do-deploy              # Primer deploy (crea la app)
make do-update              # Actualiza app existente
make do-deploy-now          # Fuerza redeploy inmediato
make do-logs                # Logs en tiempo real
make do-status              # Estado de la app

# Database
make do-db-setup            # Crea DO Managed PostgreSQL
make migrate                # Ejecuta migraciones Alembic

# Tests
make test                   # Suite completa
make gradient-test          # Solo tests de Gradient AI
```

---

## 🚨 TROUBLESHOOTING ESPECÍFICO DO

**DO Gradient AI SDK no encontrado:**
```bash
pip install gradient-ai --break-system-packages
# Verificar: python -c "from gradient import Gradient; print('OK')"
```

**Model name incorrecto:**
```python
# Ve a cloud.digitalocean.com/gen-ai → Serverless Inference → supported models
# Usa el ID exacto que aparece ahí (ej: "llama3-3-70b-instruct")
```

**DO App Platform build falla:**
```bash
# Verifica que backend/Dockerfile tiene los system deps:
# RUN apt-get install -y tesseract-ocr tesseract-ocr-spa
# Y que requirements.txt tiene gradient-ai
```

**pgvector no disponible en DO Managed PostgreSQL:**
```sql
-- Conectar a la DB managed y ejecutar:
CREATE EXTENSION IF NOT EXISTS vector;
-- Si falla, verificar versión: PostgreSQL 16 soporta pgvector natively
```

**boto3 con DO Spaces da error de endpoint:**
```python
# CORRECTO:
s3 = boto3.client('s3',
    endpoint_url='https://nyc3.digitaloceanspaces.com',
    aws_access_key_id=settings.DO_SPACES_KEY,
    aws_secret_access_key=settings.DO_SPACES_SECRET,
    region_name='nyc3'
)
```

---

## 📝 CONVENCIONES (las mismas del CLAUDE.md original)

1. SIEMPRE usa `structlog` en lugar de `print()`
2. SIEMPRE type hints y docstrings en Python
3. SIEMPRE tests junto con la implementación
4. NUNCA hardcodees API keys — usa `.env`
5. NUNCA comitees datos de pacientes reales — solo sintéticos
6. Commits semánticos: `feat(gradient):`, `feat(diagnose):`, `feat(deploy):`, `docs:`

---

*Última actualización: March 2026*  
*Versión: 2.0.0 — DO Gradient AI Hackathon Edition*  
*Autor: Said Ivan Briones Moreno — saidmoreno808*
