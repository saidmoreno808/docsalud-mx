# CLAUDE.md — DocSalud MX: Pipeline Maestro para Claude Code

> **Proyecto:** DocSalud MX — Sistema de Digitalización Inteligente de Expedientes Clínicos
> **Autor:** Said Ivan Briones Moreno
> **Fecha:** Febrero 2026
> **Nivel:** Senior AI Solutions Engineer
> **Claude Code Version:** Compatible con Claude Code CLI

---

## 🎯 PROPÓSITO DE ESTE ARCHIVO

Este archivo es la **fuente única de verdad** para Claude Code. Contiene todas las instrucciones,
convenciones, arquitectura, y el pipeline paso a paso para construir DocSalud MX de inicio a fin.
Claude Code debe leer este archivo ANTES de ejecutar cualquier tarea.

---

## 📋 ÍNDICE

1. [Visión General del Proyecto](#1-visión-general-del-proyecto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Estructura de Directorios](#3-estructura-de-directorios)
4. [Convenciones de Código](#4-convenciones-de-código)
5. [Stack Tecnológico Exacto](#5-stack-tecnológico-exacto)
6. [Variables de Entorno](#6-variables-de-entorno)
7. [Pipeline de Ejecución — Fase por Fase](#7-pipeline-de-ejecución)
8. [Fase 0: Setup del Proyecto](#fase-0-setup-del-proyecto)
9. [Fase 1: Módulo OCR y Visión Artificial](#fase-1-módulo-ocr-y-visión-artificial)
10. [Fase 2: Módulo NLP y Extracción de Entidades](#fase-2-módulo-nlp-y-extracción-de-entidades)
11. [Fase 3: Módulo ML — Clasificación y Clustering](#fase-3-módulo-ml-clasificación-y-clustering)
12. [Fase 4: Módulo RAG y LLMs](#fase-4-módulo-rag-y-llms)
13. [Fase 5: API y Microservicios](#fase-5-api-y-microservicios)
14. [Fase 6: Frontend React Dashboard](#fase-6-frontend-react-dashboard)
15. [Fase 7: DevOps, Docker y CI/CD](#fase-7-devops-docker-y-cicd)
16. [Fase 8: Deploy en AWS](#fase-8-deploy-en-aws)
17. [Fase 9: Testing y QA](#fase-9-testing-y-qa)
18. [Fase 10: Documentación y Portfolio](#fase-10-documentación-y-portfolio)
19. [Prompts Exactos para Claude Code](#prompts-exactos-para-claude-code)
20. [Troubleshooting](#troubleshooting)

---

## 1. VISIÓN GENERAL DEL PROYECTO

### Problema
En México, miles de clínicas rurales manejan expedientes médicos en papel. Esto causa:
- Pérdida de historiales clínicos
- Imposibilidad de dar seguimiento a enfermedades crónicas (diabetes, hipertensión)
- Diagnósticos duplicados y tratamientos contradictorios
- Dificultad para referencias entre niveles de atención

### Solución
DocSalud MX es un sistema de AI que:
1. Recibe fotografías o escaneos de expedientes clínicos en papel
2. Digitaliza el contenido mediante OCR + visión artificial (OpenCV)
3. Extrae información estructurada con NLP (SpaCy, HuggingFace)
4. Clasifica documentos automáticamente con ML (supervisado + no supervisado)
5. Genera alertas de pacientes en riesgo
6. Permite consultas en lenguaje natural sobre historiales (RAG + LLMs)

### Tecnologías Requeridas por la Vacante (TODAS cubiertas)
- ✅ Python (intermedio-avanzado)
- ✅ ML supervisado y no supervisado
- ✅ OCR + extracción de datos de PDFs
- ✅ SpaCy / NLTK
- ✅ BeautifulSoup
- ✅ HuggingFace Transformers
- ✅ OpenCV / CV2
- ✅ Keras, TensorFlow, PyTorch, Sklearn
- ✅ DevOps: Jenkins, Git, Docker
- ✅ Arquitecturas de microservicios (APIs)
- ✅ Git con branching strategy
- ✅ NLP
- ✅ LLMs
- ✅ GCP / AWS
- ✅ Scrum (documentado en GitHub Projects)

---

## 2. ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  Upload de docs │ Dashboard │ Alertas │ Chat NL │ Expedientes   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / REST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                         │
│              /upload  /query  /patients  /alerts                 │
│              /classify  /extract  /search  /health               │
└──────┬──────────┬──────────┬──────────┬────────────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────────────────┐
│  OCR     ││  NLP     ││   ML     ││   RAG Engine         │
│  Module  ││  Module  ││  Module  ││                      │
│          ││          ││          ││  LLM + Vector Search │
│ OpenCV   ││ SpaCy    ││ Sklearn  ││  OpenAI / Claude     │
│ Tesseract││ NLTK     ││ PyTorch  ││  Supabase pgvector   │
│ PyMuPDF  ││ HugFace  ││ TF/Keras ││                      │
└────┬─────┘└────┬─────┘└────┬─────┘└──────────┬───────────┘
     │           │           │                  │
     ▼           ▼           ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                    │
│  PostgreSQL (structured) │ Supabase pgvector (embeddings)       │
│  S3/MinIO (documents)    │ Redis (cache)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Detallado

```
INGESTA:
  Imagen/PDF → OpenCV (preprocess) → Tesseract/PyMuPDF (OCR) → Texto crudo

PROCESAMIENTO:
  Texto crudo → SpaCy NER (entidades médicas) → HuggingFace (clasificación)
             → NLTK (tokenización, limpieza) → Datos estructurados

ANÁLISIS:
  Datos estructurados → Sklearn (clasificación supervisada)
                      → PyTorch (transformer fine-tuned)
                      → TF/Keras (detección de anomalías)
                      → K-Means/DBSCAN (clustering de riesgo)

CONSULTA:
  Query del usuario → Embedding → Vector search (pgvector)
                   → Contexto recuperado → LLM → Respuesta

ALERTAS:
  Datos del paciente → Reglas + ML → Detección de riesgo → Notificación
```

---

## 3. ESTRUCTURA DE DIRECTORIOS

```
docsalud-mx/
├── CLAUDE.md                          # ← ESTE ARCHIVO
├── README.md                          # Documentación pública del proyecto
├── LICENSE                            # MIT License
├── .gitignore
├── .env.example                       # Template de variables de entorno
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # GitHub Actions CI pipeline
│   │   ├── cd.yml                     # GitHub Actions CD pipeline
│   │   └── tests.yml                  # Test automation
│   └── PULL_REQUEST_TEMPLATE.md
├── docker-compose.yml                 # Orquestación local completa
├── docker-compose.prod.yml            # Orquestación producción
├── Makefile                           # Comandos útiles del proyecto
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt               # Dependencias Python pinned
│   ├── requirements-dev.txt           # Dependencias de desarrollo
│   ├── pyproject.toml                 # Configuración del proyecto Python
│   ├── setup.cfg                      # Configuración de linters
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Entry point FastAPI
│   │   ├── config.py                  # Configuración centralizada
│   │   ├── dependencies.py            # Inyección de dependencias
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py          # Router principal v1
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── upload.py      # POST /upload — subida de documentos
│   │   │   │   │   ├── patients.py    # CRUD pacientes
│   │   │   │   │   ├── documents.py   # CRUD documentos procesados
│   │   │   │   │   ├── search.py      # GET /search — búsqueda semántica
│   │   │   │   │   ├── query.py       # POST /query — chat RAG
│   │   │   │   │   ├── alerts.py      # GET /alerts — alertas de riesgo
│   │   │   │   │   ├── classify.py    # POST /classify — clasificación ML
│   │   │   │   │   └── health.py      # GET /health — healthcheck
│   │   │   │   └── schemas/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── upload.py      # Pydantic models para upload
│   │   │   │       ├── patient.py     # Pydantic models para pacientes
│   │   │   │       ├── document.py    # Pydantic models para documentos
│   │   │   │       ├── query.py       # Pydantic models para queries
│   │   │   │       └── alert.py       # Pydantic models para alertas
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── cors.py
│   │   │       ├── logging.py
│   │   │       └── rate_limit.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── ocr/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── preprocessor.py    # OpenCV preprocessing pipeline
│   │   │   │   ├── extractor.py       # Tesseract + PyMuPDF OCR engine
│   │   │   │   ├── pdf_handler.py     # Manejo específico de PDFs
│   │   │   │   └── image_handler.py   # Manejo de imágenes (foto de celular)
│   │   │   │
│   │   │   ├── nlp/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pipeline.py        # Pipeline NLP principal
│   │   │   │   ├── ner_extractor.py   # SpaCy NER médico
│   │   │   │   ├── text_cleaner.py    # NLTK tokenización y limpieza
│   │   │   │   ├── classifier.py      # HuggingFace document classifier
│   │   │   │   └── entity_linker.py   # Vinculación de entidades a CIE-10
│   │   │   │
│   │   │   ├── ml/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── document_classifier.py   # Sklearn Random Forest + SVM
│   │   │   │   ├── anomaly_detector.py      # TF/Keras autoencoder
│   │   │   │   ├── risk_clusterer.py        # K-Means/DBSCAN clustering
│   │   │   │   ├── transformer_classifier.py # PyTorch fine-tuned BERT
│   │   │   │   ├── feature_engineering.py   # Feature extraction pipeline
│   │   │   │   └── model_registry.py        # Carga y versionado de modelos
│   │   │   │
│   │   │   ├── rag/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── embedder.py        # Generación de embeddings
│   │   │   │   ├── vector_store.py    # Supabase pgvector interface
│   │   │   │   ├── retriever.py       # Retrieval pipeline
│   │   │   │   ├── generator.py       # LLM response generation
│   │   │   │   ├── chain.py           # RAG chain completo
│   │   │   │   └── prompts.py         # System prompts y templates
│   │   │   │
│   │   │   └── alerts/
│   │   │       ├── __init__.py
│   │   │       ├── rules_engine.py    # Reglas clínicas de alerta
│   │   │       ├── risk_scorer.py     # Scoring de riesgo por paciente
│   │   │       └── notifier.py        # Sistema de notificaciones
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # Conexión a PostgreSQL
│   │   │   ├── models.py              # SQLAlchemy ORM models
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── patient_repo.py
│   │   │   │   ├── document_repo.py
│   │   │   │   └── alert_repo.py
│   │   │   └── migrations/
│   │   │       └── ... (Alembic migrations)
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py    # Orquesta el pipeline completo
│   │   │   ├── patient_service.py     # Lógica de negocio de pacientes
│   │   │   ├── search_service.py      # Búsqueda semántica
│   │   │   └── alert_service.py       # Lógica de alertas
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py              # Logging estructurado
│   │       ├── scraper.py             # BeautifulSoup scraper medicamentos
│   │       └── validators.py          # Validaciones comunes
│   │
│   ├── models/                        # Modelos ML pre-entrenados/fine-tuned
│   │   ├── .gitkeep
│   │   ├── document_classifier/       # Sklearn models serializados
│   │   ├── ner_medical/               # SpaCy custom NER model
│   │   ├── anomaly_detector/          # TF/Keras saved model
│   │   └── transformer_classifier/    # PyTorch fine-tuned model
│   │
│   ├── data/
│   │   ├── raw/                       # Datos crudos (no commitear)
│   │   ├── processed/                 # Datos procesados
│   │   ├── training/                  # Datasets de entrenamiento
│   │   │   ├── document_types/        # Ejemplos por tipo de documento
│   │   │   ├── ner_annotations/       # Anotaciones NER formato SpaCy
│   │   │   └── lab_results/           # Resultados de laboratorio ejemplo
│   │   ├── synthetic/                 # Datos sintéticos generados
│   │   └── reference/
│   │       ├── cie10_codes.json       # Catálogo CIE-10
│   │       ├── medications.json       # Cuadro básico de medicamentos
│   │       └── lab_ranges.json        # Rangos normales de laboratorio
│   │
│   ├── notebooks/                     # Jupyter notebooks de exploración
│   │   ├── 01_ocr_exploration.ipynb
│   │   ├── 02_ner_training.ipynb
│   │   ├── 03_classifier_training.ipynb
│   │   ├── 04_clustering_analysis.ipynb
│   │   ├── 05_rag_evaluation.ipynb
│   │   └── 06_model_comparison.ipynb
│   │
│   ├── scripts/
│   │   ├── generate_synthetic_data.py # Genera datos de entrenamiento sintéticos
│   │   ├── train_ner_model.py         # Entrena modelo NER SpaCy
│   │   ├── train_classifier.py        # Entrena clasificadores ML
│   │   ├── train_transformer.py       # Fine-tune transformer
│   │   ├── scrape_medications.py      # Scraper BeautifulSoup
│   │   ├── seed_database.py           # Seed de datos iniciales
│   │   └── evaluate_models.py         # Evaluación comparativa de modelos
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                # Fixtures compartidos
│       ├── unit/
│       │   ├── test_ocr_preprocessor.py
│       │   ├── test_ner_extractor.py
│       │   ├── test_classifier.py
│       │   ├── test_rag_chain.py
│       │   └── test_alert_rules.py
│       ├── integration/
│       │   ├── test_upload_pipeline.py
│       │   ├── test_search_endpoint.py
│       │   └── test_query_endpoint.py
│       └── e2e/
│           └── test_full_pipeline.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .eslintrc.js
│   ├── public/
│   │   └── assets/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Header.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── MainLayout.tsx
│       │   ├── upload/
│       │   │   ├── DocumentUploader.tsx
│       │   │   ├── CameraCapture.tsx
│       │   │   └── UploadProgress.tsx
│       │   ├── dashboard/
│       │   │   ├── StatsCards.tsx
│       │   │   ├── RecentDocuments.tsx
│       │   │   ├── AlertsPanel.tsx
│       │   │   └── RiskChart.tsx
│       │   ├── patients/
│       │   │   ├── PatientList.tsx
│       │   │   ├── PatientDetail.tsx
│       │   │   └── PatientTimeline.tsx
│       │   ├── documents/
│       │   │   ├── DocumentViewer.tsx
│       │   │   ├── ExtractedData.tsx
│       │   │   └── DocumentComparison.tsx
│       │   ├── chat/
│       │   │   ├── ChatInterface.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   └── QuerySuggestions.tsx
│       │   └── common/
│       │       ├── LoadingSpinner.tsx
│       │       ├── ErrorBoundary.tsx
│       │       └── ConfirmDialog.tsx
│       ├── hooks/
│       │   ├── useUpload.ts
│       │   ├── usePatients.ts
│       │   ├── useSearch.ts
│       │   └── useChat.ts
│       ├── services/
│       │   └── api.ts                 # Axios client con interceptors
│       ├── types/
│       │   └── index.ts               # TypeScript types globales
│       └── utils/
│           └── formatters.ts
│
├── infrastructure/
│   ├── terraform/                     # IaC (opcional, para AWS)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── nginx/
│   │   └── nginx.conf                 # Reverse proxy config
│   └── scripts/
│       ├── deploy.sh                  # Script de deploy
│       ├── backup.sh                  # Backup de DB
│       └── setup-server.sh            # Setup inicial del servidor
│
└── docs/
    ├── architecture.md                # Diagrama y decisiones de arquitectura
    ├── api-spec.md                    # Especificación de API
    ├── deployment-guide.md            # Guía de deploy
    ├── model-cards/                   # Documentación de cada modelo ML
    │   ├── document-classifier.md
    │   ├── ner-medical.md
    │   ├── anomaly-detector.md
    │   └── risk-clusterer.md
    └── sprint-retrospectives/         # Documentación Scrum
        ├── sprint-1.md
        └── ...
```

---

## 4. CONVENCIONES DE CÓDIGO

### Python (Backend)
- **Formatter:** Black (line length 100)
- **Linter:** Ruff
- **Type checking:** mypy (strict mode)
- **Import sorting:** isort (compatible con Black)
- **Docstrings:** Google style
- **Naming:**
  - Archivos: `snake_case.py`
  - Clases: `PascalCase`
  - Funciones/variables: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`
  - Privados: `_prefixed_with_underscore`
- **Cada función DEBE tener:**
  - Type hints en parámetros y retorno
  - Docstring con descripción, Args, Returns, Raises
  - Máximo 30 líneas (refactorizar si excede)
- **Cada módulo DEBE tener:**
  - Docstring al inicio explicando su propósito
  - `__all__` definido en `__init__.py`

### TypeScript (Frontend)
- **Framework:** React 18+ con TypeScript
- **Styling:** Tailwind CSS
- **State management:** React Query + Zustand (si necesario)
- **Naming:**
  - Componentes: `PascalCase.tsx`
  - Hooks: `useCamelCase.ts`
  - Utilidades: `camelCase.ts`
  - Types: `PascalCase`

### Git
- **Branching:** GitFlow
  - `main` — producción estable
  - `develop` — integración
  - `feature/DSM-XXX-descripcion` — features nuevas
  - `bugfix/DSM-XXX-descripcion` — corrección de bugs
  - `hotfix/DSM-XXX-descripcion` — fix urgente en producción
  - `release/vX.X.X` — preparación de release
- **Commits:** Conventional Commits
  - `feat(ocr): add adaptive thresholding for handwritten docs`
  - `fix(nlp): correct SpaCy NER entity alignment issue`
  - `docs(readme): add architecture diagram`
  - `test(ml): add unit tests for document classifier`
  - `chore(docker): update Python base image to 3.11`
  - `refactor(api): extract upload validation to middleware`
- **Pull Requests:**
  - Título descriptivo
  - Descripción del cambio y por qué
  - Screenshots si hay cambios visuales
  - Al menos self-review antes de merge

### Logging
- Usar `structlog` para logging estructurado en JSON
- Niveles: DEBUG en dev, INFO en producción
- Cada request debe tener un `correlation_id`
- Nunca loggear datos sensibles de pacientes (PII)

### Error Handling
- Excepciones custom en `app/core/exceptions.py`
- Nunca silenciar excepciones con `except: pass`
- Siempre retornar respuestas HTTP apropiadas con mensajes claros
- Errores de ML deben incluir métricas de confianza

---

## 5. STACK TECNOLÓGICO EXACTO

### Backend
```
# requirements.txt — VERSIONES EXACTAS

# === FastAPI y servidor ===
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
python-multipart==0.0.19
httpx==0.28.1

# === OCR y Visión Artificial ===
opencv-python-headless==4.10.0.84
pytesseract==0.3.13
Pillow==11.1.0
PyMuPDF==1.25.3
pdf2image==1.17.0

# === NLP ===
spacy==3.8.4
nltk==3.9.1
beautifulsoup4==4.12.3
requests==2.32.3

# === HuggingFace ===
transformers==4.47.1
tokenizers==0.21.0
datasets==3.2.0
accelerate==1.2.1
sentencepiece==0.2.0

# === Machine Learning ===
scikit-learn==1.6.1
torch==2.5.1
tensorflow==2.18.0
keras==3.8.0
numpy==1.26.4
pandas==2.2.3
scipy==1.15.1
joblib==1.4.2
xgboost==2.1.3

# === Visualización (para notebooks) ===
matplotlib==3.10.0
seaborn==0.13.2
plotly==5.24.1

# === RAG y LLMs ===
openai==1.58.1
anthropic==0.42.0
langchain==0.3.14
langchain-community==0.3.14
langchain-openai==0.3.0

# === Base de datos ===
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.1
supabase==2.12.0
pgvector==0.3.6

# === Cache ===
redis==5.2.1

# === DevOps y Monitoreo ===
prometheus-client==0.21.1
structlog==24.4.0

# === Testing ===
pytest==8.3.4
pytest-asyncio==0.25.0
pytest-cov==6.0.0
httpx==0.28.1

# === Calidad de código ===
black==24.10.0
ruff==0.8.6
mypy==1.14.1
isort==5.13.2
pre-commit==4.0.1
```

### Frontend
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^7.1.1",
    "@tanstack/react-query": "^5.62.8",
    "axios": "^1.7.9",
    "tailwindcss": "^3.4.17",
    "lucide-react": "^0.469.0",
    "recharts": "^2.15.0",
    "react-dropzone": "^14.3.5",
    "zustand": "^5.0.3",
    "date-fns": "^4.1.0",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.18",
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.7",
    "typescript": "^5.7.3",
    "eslint": "^9.17.0",
    "@testing-library/react": "^16.1.0",
    "vitest": "^2.1.8"
  }
}
```

---

## 6. VARIABLES DE ENTORNO

```bash
# .env.example — Copiar a .env y llenar valores

# === App ===
APP_NAME=docsalud-mx
APP_ENV=development  # development | staging | production
APP_DEBUG=true
APP_PORT=8000
APP_HOST=0.0.0.0
SECRET_KEY=your-secret-key-here-change-in-production
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# === Database ===
DATABASE_URL=postgresql+asyncpg://docsalud:password@localhost:5432/docsalud_db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# === Supabase (Vector Store) ===
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# === Redis ===
REDIS_URL=redis://localhost:6379/0

# === OpenAI ===
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# === Anthropic ===
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# === Tesseract ===
TESSERACT_CMD=/usr/bin/tesseract
TESSERACT_LANG=spa

# === AWS (Production) ===
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=docsalud-mx-documents

# === Logging ===
LOG_LEVEL=DEBUG  # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json

# === ML Models ===
MODEL_PATH=./models
NER_MODEL_PATH=./models/ner_medical
CLASSIFIER_MODEL_PATH=./models/document_classifier
ANOMALY_MODEL_PATH=./models/anomaly_detector
```

---

## 7. PIPELINE DE EJECUCIÓN

### Orden estricto de fases

```
FASE 0: Setup         → Estructura, Git, Docker base, DB
FASE 1: OCR           → OpenCV + Tesseract + PyMuPDF
FASE 2: NLP           → SpaCy + NLTK + HuggingFace + BeautifulSoup
FASE 3: ML            → Sklearn + PyTorch + TF/Keras (supervisado + no supervisado)
FASE 4: RAG           → Embeddings + pgvector + LLMs
FASE 5: API           → FastAPI microservicios
FASE 6: Frontend      → React dashboard
FASE 7: DevOps        → Docker + CI/CD + Monitoreo
FASE 8: Deploy        → AWS EC2
FASE 9: Testing       → Unit + Integration + E2E
FASE 10: Docs         → README, Model Cards, Portfolio
```

### Regla de oro
> **Cada fase DEBE tener tests antes de pasar a la siguiente.**
> **Cada fase DEBE tener un commit con tag semántico.**

---

## FASE 0: SETUP DEL PROYECTO

### 0.1 — Inicializar repositorio

```bash
# Claude Code prompt:
# "Inicializa el repositorio Git con la estructura de directorios completa
#  definida en CLAUDE.md sección 3. Crea todos los __init__.py, .gitignore
#  robusto para Python/Node/Docker, .env.example, y el README.md inicial."

mkdir docsalud-mx && cd docsalud-mx
git init
git checkout -b main
```

**Claude Code debe crear:**
1. Toda la estructura de directorios con archivos vacíos
2. `.gitignore` completo (Python, Node, Docker, .env, models/, data/raw/)
3. `.env.example` con todas las variables documentadas
4. `README.md` con badges, descripción, setup rápido
5. `LICENSE` (MIT)
6. `Makefile` con comandos: `make setup`, `make dev`, `make test`, `make lint`, `make docker-up`

### 0.2 — Docker Compose base

```yaml
# docker-compose.yml que Claude Code debe generar:
# - PostgreSQL 16 con pgvector extension
# - Redis 7
# - Backend (Python 3.11, con Tesseract instalado)
# - Frontend (Node 20, Vite dev server)
# - Volúmenes para persistencia y hot-reload
```

**Especificaciones del Dockerfile backend:**
```dockerfile
# Base: python:3.11-slim
# Instalar: tesseract-ocr tesseract-ocr-spa libgl1-mesa-glx libglib2.0-0 poppler-utils
# Copiar requirements.txt e instalar dependencias
# SpaCy: descargar modelo es_core_news_lg
# NLTK: descargar punkt, stopwords, wordnet (español)
# Working directory: /app
# CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 0.3 — Base de datos

**Schema PostgreSQL inicial que Claude Code debe crear (Alembic migration):**

```sql
-- Tabla: patients
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(50) UNIQUE,           -- CURP o ID de clínica
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    blood_type VARCHAR(5),
    chronic_conditions JSONB DEFAULT '[]',     -- ["diabetes_tipo_2", "hipertension"]
    risk_score FLOAT DEFAULT 0.0,              -- 0.0 a 1.0
    risk_cluster INTEGER,                       -- Cluster asignado por ML
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,        -- 'receta', 'laboratorio', 'nota_medica', 'referencia'
    document_type_confidence FLOAT,             -- Confianza del clasificador
    original_filename VARCHAR(255),
    storage_path VARCHAR(500),                  -- Ruta en S3/local
    raw_text TEXT,                               -- Texto extraído por OCR
    ocr_confidence FLOAT,                       -- Confianza promedio del OCR
    extracted_data JSONB,                        -- Datos estructurados extraídos
    processing_status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: extracted_entities
CREATE TABLE extracted_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,          -- 'medicamento', 'diagnostico', 'dosis', 'fecha', 'signo_vital'
    entity_value TEXT NOT NULL,
    normalized_value TEXT,                       -- Valor normalizado (ej: código CIE-10)
    confidence FLOAT,
    start_char INTEGER,                         -- Posición en texto original
    end_char INTEGER,
    metadata JSONB DEFAULT '{}'
);

-- Tabla: alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id),
    alert_type VARCHAR(50) NOT NULL,           -- 'glucosa_alta', 'sin_seguimiento', 'interaccion_medicamentos'
    severity VARCHAR(10) NOT NULL,              -- 'low', 'medium', 'high', 'critical'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: document_embeddings (pgvector)
CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536),                     -- OpenAI text-embedding-3-small dimension
    metadata JSONB DEFAULT '{}'
);

-- Índices
CREATE INDEX idx_documents_patient ON documents(patient_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_entities_document ON extracted_entities(document_id);
CREATE INDEX idx_entities_type ON extracted_entities(entity_type);
CREATE INDEX idx_alerts_patient ON alerts(patient_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_unresolved ON alerts(is_resolved) WHERE is_resolved = FALSE;

-- Índice vectorial para búsqueda semántica
CREATE INDEX idx_embeddings_vector ON document_embeddings
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 0.4 — Commit inicial

```bash
git add .
git commit -m "chore: initial project setup with full directory structure, Docker, and DB schema"
git tag v0.1.0
git checkout -b develop
```

---

## FASE 1: MÓDULO OCR Y VISIÓN ARTIFICIAL

> **Objetivo:** Recibir imágenes o PDFs de expedientes clínicos y extraer texto limpio.
> **Tecnologías:** OpenCV, Tesseract, PyMuPDF, Pillow, pdf2image

### 1.1 — OpenCV Preprocessor (`backend/app/core/ocr/preprocessor.py`)

**Claude Code debe implementar estas funciones:**

```python
"""
Módulo de preprocesamiento de imágenes para OCR.
Usa OpenCV para mejorar la calidad de imágenes antes de OCR.
Optimizado para documentos médicos escaneados y fotos de celular.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple

class ImagePreprocessor:
    """Pipeline de preprocesamiento de imágenes para OCR médico."""

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Pipeline completo de preprocesamiento.

        Pasos:
        1. Resize si es muy grande (max 3000px lado largo)
        2. Convertir a escala de grises
        3. Corrección de rotación (deskew)
        4. Eliminación de ruido (denoising)
        5. Binarización adaptativa
        6. Corrección de perspectiva (si aplica)
        7. Detección y recorte de región de interés

        Args:
            image: Imagen en formato numpy array (BGR)

        Returns:
            Imagen preprocesada lista para OCR
        """
        pass

    def resize_if_needed(self, image: np.ndarray, max_dim: int = 3000) -> np.ndarray:
        """Redimensiona manteniendo aspect ratio si excede max_dim."""
        pass

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convierte a escala de grises."""
        pass

    def deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Corrige rotación del documento.
        Usa Hough Line Transform para detectar líneas y calcular ángulo.
        Rota la imagen para corregir.
        """
        pass

    def denoise(self, image: np.ndarray) -> np.ndarray:
        """
        Elimina ruido usando cv2.fastNlMeansDenoising.
        Parámetros calibrados para documentos médicos.
        """
        pass

    def adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """
        Binarización adaptativa con cv2.adaptiveThreshold.
        Usa ADAPTIVE_THRESH_GAUSSIAN_C con blockSize=11 y C=2.
        """
        pass

    def detect_text_regions(self, image: np.ndarray) -> list[Tuple[int, int, int, int]]:
        """
        Detecta regiones de texto usando contornos.
        Retorna lista de bounding boxes (x, y, w, h).
        Útil para segmentar secciones del expediente.
        """
        pass

    def correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """
        Corrige perspectiva si la foto fue tomada en ángulo.
        Detecta los 4 corners del documento y aplica warpPerspective.
        """
        pass

    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Mejora contraste con CLAHE (Contrast Limited Adaptive Histogram Equalization).
        clipLimit=2.0, tileGridSize=(8,8).
        """
        pass
```

### 1.2 — OCR Extractor (`backend/app/core/ocr/extractor.py`)

```python
"""
Motor de OCR que combina Tesseract y PyMuPDF.
Tesseract para imágenes, PyMuPDF para PDFs nativos.
"""

class OCRExtractor:
    """Extractor de texto mediante OCR."""

    def extract_from_image(self, image_path: str) -> OCRResult:
        """
        Extrae texto de una imagen.
        1. Carga imagen con OpenCV
        2. Preprocesa con ImagePreprocessor
        3. Ejecuta Tesseract con config: --oem 3 --psm 6 -l spa
        4. Obtiene texto + confianza por palabra
        5. Retorna OCRResult con texto, confianza promedio, y bounding boxes
        """
        pass

    def extract_from_pdf(self, pdf_path: str) -> OCRResult:
        """
        Extrae texto de PDF.
        1. Intenta extracción directa con PyMuPDF (para PDFs nativos)
        2. Si no hay texto (PDF escaneado), convierte a imágenes con pdf2image
        3. Aplica OCR a cada página
        4. Combina resultados
        """
        pass

    def extract_with_layout(self, image_path: str) -> list[TextBlock]:
        """
        Extracción con información de layout.
        Usa Tesseract con output_type=dict para obtener posiciones.
        Agrupa palabras en bloques/líneas.
        Útil para entender estructura del documento.
        """
        pass
```

**Dataclasses que debe crear:**
```python
@dataclass
class OCRResult:
    text: str                          # Texto completo extraído
    confidence: float                  # Confianza promedio (0-100)
    page_count: int                    # Número de páginas
    blocks: list[TextBlock]            # Bloques con posición
    processing_time_ms: int            # Tiempo de procesamiento
    warnings: list[str]                # Advertencias (baja confianza, etc.)

@dataclass
class TextBlock:
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]    # x, y, w, h
    page: int
    block_type: str                    # 'paragraph', 'header', 'table_cell'
```

### 1.3 — Tests OCR

```python
# tests/unit/test_ocr_preprocessor.py
# Claude Code debe crear tests para:
# - test_grayscale_conversion: verificar que output es 1 canal
# - test_deskew_corrects_rotation: imagen rotada 5° debe corregirse
# - test_adaptive_threshold_binary: output solo tiene valores 0 y 255
# - test_denoise_reduces_noise: SNR mejora después de denoising
# - test_detect_text_regions_finds_blocks: imagen con texto debe detectar ≥1 región
# - test_preprocess_pipeline_end_to_end: imagen completa pasa todo el pipeline

# tests/unit/test_ocr_extractor.py
# - test_extract_from_clear_image: imagen clara debe tener confianza >80%
# - test_extract_from_pdf_native: PDF con texto nativo extrae sin OCR
# - test_extract_from_pdf_scanned: PDF escaneado usa OCR fallback
# - test_extract_returns_valid_result: resultado tiene todos los campos
```

### 1.4 — Commit fase 1

```bash
git checkout -b feature/DSM-001-ocr-module
# ... desarrollo ...
git add .
git commit -m "feat(ocr): implement OpenCV preprocessing pipeline and Tesseract/PyMuPDF extraction"
git checkout develop
git merge feature/DSM-001-ocr-module
git tag v0.2.0
```

---

## FASE 2: MÓDULO NLP Y EXTRACCIÓN DE ENTIDADES

> **Objetivo:** Extraer entidades médicas del texto OCR y clasificar documentos.
> **Tecnologías:** SpaCy, NLTK, HuggingFace Transformers, BeautifulSoup

### 2.1 — Generación de datos sintéticos (`scripts/generate_synthetic_data.py`)

**CRÍTICO: Necesitamos datos de entrenamiento. Claude Code debe generar datos sintéticos realistas.**

```python
"""
Genera datos sintéticos de expedientes médicos mexicanos para entrenamiento.

Tipos de documentos:
1. Recetas médicas — medicamento, dosis, frecuencia, duración
2. Resultados de laboratorio — glucosa, colesterol, biometría hemática
3. Notas médicas — diagnóstico, exploración física, plan de tratamiento
4. Referencias/Contrarreferencias — motivo, dx, tratamiento previo

Debe generar:
- 500+ ejemplos por tipo de documento (2000+ total)
- Anotaciones NER en formato SpaCy (entidades con offsets)
- Variaciones realistas (abreviaturas médicas, letra difícil, errores de OCR)
- Datos demográficos mexicanos realistas (nombres, CURP, direcciones SLP)
"""

# Ejemplo de receta generada:
RECETA_TEMPLATE = """
Dr. {nombre_doctor}
Cédula Profesional: {cedula}
{especialidad}

Paciente: {nombre_paciente}
Edad: {edad} años    Sexo: {sexo}
Fecha: {fecha}

Rx:
1. {medicamento_1} {presentacion_1}
   {dosis_1} cada {frecuencia_1} por {duracion_1}
2. {medicamento_2} {presentacion_2}
   {dosis_2} cada {frecuencia_2} por {duracion_2}

Dx: {diagnostico}

Próxima cita: {fecha_cita}

_________________________
Firma del médico
"""

# NER annotations formato SpaCy:
# ("Metformina 850mg tabletas\n   1 tableta cada 12 horas por 30 días",
#  {"entities": [
#      (0, 10, "MEDICAMENTO"),
#      (11, 16, "DOSIS"),
#      (17, 25, "PRESENTACION"),
#      (31, 40, "FRECUENCIA_DOSIS"),
#      (45, 52, "FRECUENCIA_TIEMPO"),
#      (57, 64, "DURACION")
#  ]})
```

**Entidades NER a definir:**
```
MEDICAMENTO        — Nombre del medicamento
DOSIS              — Cantidad (850mg, 500mg, 10ml)
PRESENTACION       — Forma farmacéutica (tabletas, cápsulas, jarabe)
FRECUENCIA_DOSIS   — Cantidad por toma (1 tableta, 2 cápsulas)
FRECUENCIA_TIEMPO  — Cada cuánto (cada 8 horas, cada 12 horas)
DURACION           — Duración del tratamiento (30 días, 2 semanas)
DIAGNOSTICO        — Diagnóstico (Diabetes Mellitus tipo 2)
CODIGO_CIE10       — Código CIE-10 (E11.9)
SIGNO_VITAL        — Tipo de medición (glucosa, presión arterial)
VALOR_MEDICION     — Valor numérico (126 mg/dL, 140/90 mmHg)
RANGO_REFERENCIA   — Rango normal (70-100 mg/dL)
NOMBRE_PACIENTE    — Nombre del paciente
NOMBRE_MEDICO      — Nombre del médico
FECHA              — Cualquier fecha en el documento
INSTITUCION        — Nombre de la clínica/hospital
```

### 2.2 — BeautifulSoup Scraper (`backend/app/utils/scraper.py`)

```python
"""
Scraper de referencia médica usando BeautifulSoup.

Fuentes:
1. Cuadro Básico de Medicamentos del IMSS (lista oficial)
2. Catálogo CIE-10 en español
3. Vademécum farmacológico

El scraper debe:
- Obtener lista de medicamentos del cuadro básico
- Extraer: nombre genérico, nombre comercial, presentación, indicaciones
- Guardar en data/reference/medications.json
- Manejar errores de red y rate limiting
- Cachear resultados para no sobrecargar servidores
"""

from bs4 import BeautifulSoup
import requests
import json
import time

class MedicalReferenceScraper:
    """Scraper de referencias médicas mexicanas."""

    def scrape_medications(self) -> list[dict]:
        """Scrapea cuadro básico de medicamentos."""
        pass

    def scrape_cie10_codes(self) -> list[dict]:
        """Scrapea catálogo CIE-10 en español."""
        pass

    def _fetch_with_retry(self, url: str, max_retries: int = 3) -> str:
        """Fetch con retry y backoff exponencial."""
        pass
```

### 2.3 — NLTK Text Cleaner (`backend/app/core/nlp/text_cleaner.py`)

```python
"""
Limpieza y normalización de texto OCR usando NLTK.
"""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

class TextCleaner:
    """Limpieza de texto extraído por OCR."""

    def __init__(self):
        self.stemmer = SnowballStemmer("spanish")
        self.stop_words = set(stopwords.words("spanish"))

    def clean(self, text: str) -> CleanedText:
        """
        Pipeline de limpieza:
        1. Normalizar unicode y encoding
        2. Corregir artefactos comunes de OCR (|→l, 0→O, rn→m)
        3. Normalizar espacios y saltos de línea
        4. Tokenizar en oraciones (sent_tokenize)
        5. Tokenizar en palabras (word_tokenize)
        6. Identificar secciones del documento
        """
        pass

    def fix_ocr_artifacts(self, text: str) -> str:
        """Corrige errores comunes de OCR en documentos médicos."""
        pass

    def normalize_medical_abbreviations(self, text: str) -> str:
        """
        Expande abreviaturas médicas comunes:
        Dx → Diagnóstico, Tx → Tratamiento, Rx → Receta,
        c/ → cada, VO → vía oral, mg → miligramos, etc.
        """
        pass

    def segment_document_sections(self, text: str) -> dict[str, str]:
        """
        Identifica secciones del documento:
        - encabezado, datos_paciente, prescripcion, diagnostico, firma
        """
        pass
```

### 2.4 — SpaCy NER Extractor (`backend/app/core/nlp/ner_extractor.py`)

```python
"""
Extractor de entidades nombradas médicas con SpaCy.
Usa modelo base es_core_news_lg + entrenamiento custom con datos médicos.
"""

import spacy
from spacy.tokens import DocBin

class MedicalNERExtractor:
    """Extractor NER especializado en documentos médicos mexicanos."""

    def __init__(self, model_path: str = None):
        """
        Carga modelo SpaCy.
        Si model_path apunta a modelo custom, lo usa.
        Si no, usa es_core_news_lg como base.
        """
        pass

    def extract_entities(self, text: str) -> list[MedicalEntity]:
        """
        Extrae entidades médicas del texto.
        Retorna lista de MedicalEntity con tipo, valor, confianza, posición.
        """
        pass

    def extract_structured_data(self, text: str, doc_type: str) -> dict:
        """
        Extrae datos estructurados según tipo de documento.

        Para 'receta':
            {medicamentos: [{nombre, dosis, frecuencia, duracion}], diagnostico, medico, fecha}

        Para 'laboratorio':
            {resultados: [{analisis, valor, unidad, rango_referencia, es_anormal}], fecha}

        Para 'nota_medica':
            {diagnostico, exploracion_fisica, signos_vitales, plan, medico, fecha}
        """
        pass

    @staticmethod
    def train_custom_model(training_data_path: str, output_path: str, n_iter: int = 30):
        """
        Entrena modelo NER custom con datos anotados.

        Pasos:
        1. Cargar datos de entrenamiento (formato SpaCy DocBin)
        2. Crear pipeline NER sobre es_core_news_lg
        3. Agregar labels custom (MEDICAMENTO, DOSIS, etc.)
        4. Entrenar con mini-batches y dropout
        5. Evaluar en set de validación
        6. Guardar mejor modelo
        """
        pass
```

### 2.5 — HuggingFace Document Classifier (`backend/app/core/nlp/classifier.py`)

```python
"""
Clasificador de documentos médicos usando HuggingFace Transformers.
Fine-tunea modelo BERT en español para clasificar tipo de documento.
"""

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

class DocumentClassifier:
    """Clasificador de tipo de documento médico con Transformers."""

    # Modelo base: dccuchile/bert-base-spanish-wwm-cased
    # o PlanTL-GOB-ES/roberta-base-biomedical-clinical-es (mejor para médico)
    BASE_MODEL = "PlanTL-GOB-ES/roberta-base-biomedical-clinical-es"

    LABELS = {
        0: "receta",
        1: "laboratorio",
        2: "nota_medica",
        3: "referencia",
        4: "consentimiento",
        5: "otro"
    }

    def classify(self, text: str) -> ClassificationResult:
        """
        Clasifica el tipo de documento.
        Retorna label + probabilidades de cada clase.
        """
        pass

    @staticmethod
    def fine_tune(
        train_dataset_path: str,
        eval_dataset_path: str,
        output_dir: str,
        epochs: int = 5,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ):
        """
        Fine-tunea el modelo con datos de documentos médicos.

        Training args:
        - evaluation_strategy="epoch"
        - save_strategy="epoch"
        - load_best_model_at_end=True
        - metric_for_best_model="f1"
        - fp16=True (si GPU disponible)
        """
        pass
```

### 2.6 — Tests NLP

```python
# Tests que Claude Code debe implementar:

# test_text_cleaner.py
# - test_fix_ocr_artifacts: "M3tformina" → "Metformina"
# - test_normalize_abbreviations: "Dx: DM2" → "Diagnóstico: Diabetes Mellitus tipo 2"
# - test_segment_sections: documento completo segmenta correctamente
# - test_clean_pipeline: texto sucio sale limpio y tokenizado

# test_ner_extractor.py
# - test_extract_medication: "Metformina 850mg" → MEDICAMENTO + DOSIS
# - test_extract_diagnosis: "Dx: Diabetes Mellitus tipo 2 (E11.9)" → DIAGNOSTICO + CIE10
# - test_extract_lab_values: "Glucosa: 126 mg/dL (70-100)" → SIGNO_VITAL + VALOR + RANGO
# - test_structured_receta: receta completa extrae todos los campos
# - test_structured_laboratorio: resultados de lab extraen correctamente

# test_classifier.py
# - test_classify_receta: texto de receta clasifica como "receta" con >80% confianza
# - test_classify_laboratorio: resultados de lab clasifican correctamente
# - test_classify_nota_medica: nota médica clasifica correctamente
```

### 2.7 — Commit fase 2

```bash
git checkout -b feature/DSM-002-nlp-module
git commit -m "feat(nlp): implement SpaCy NER, NLTK cleaner, HuggingFace classifier, and BS4 scraper"
git tag v0.3.0
```

---

## FASE 3: MÓDULO ML — CLASIFICACIÓN Y CLUSTERING

> **Objetivo:** ML supervisado para clasificación + ML no supervisado para análisis de riesgo.
> **Tecnologías:** Scikit-learn, PyTorch, TensorFlow/Keras, XGBoost

### 3.1 — Feature Engineering (`backend/app/core/ml/feature_engineering.py`)

```python
"""
Extracción de features de documentos procesados para modelos ML.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
import numpy as np
import pandas as pd

class FeatureEngineer:
    """Pipeline de feature engineering para documentos médicos."""

    def extract_text_features(self, text: str) -> np.ndarray:
        """
        Features basadas en texto:
        - TF-IDF (max_features=5000)
        - Longitud del texto
        - Número de oraciones
        - Número de entidades detectadas por tipo
        - Ratio de números vs texto
        - Presencia de keywords médicos
        """
        pass

    def extract_patient_features(self, patient_data: dict) -> np.ndarray:
        """
        Features del paciente para clustering de riesgo:
        - Edad
        - Género (one-hot)
        - Número de condiciones crónicas
        - Número de medicamentos activos
        - Frecuencia de visitas (últimos 6 meses)
        - Valores de laboratorio más recientes (normalizados)
        - Número de alertas previas
        - Tiempo desde última consulta
        """
        pass

    def extract_lab_features(self, lab_results: list[dict]) -> np.ndarray:
        """
        Features de resultados de laboratorio:
        - Valores normalizados de cada analito
        - Tendencia (subiendo/bajando/estable)
        - Distancia al rango normal
        - Número de valores fuera de rango
        """
        pass
```

### 3.2 — Clasificador Supervisado con Sklearn (`backend/app/core/ml/document_classifier.py`)

```python
"""
Clasificador de documentos con ML tradicional (Sklearn).
Complementa al clasificador HuggingFace como fallback y para comparación.
"""

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
import joblib

class SklearnDocumentClassifier:
    """Clasificador de documentos con ensemble de modelos Sklearn."""

    def __init__(self):
        self.models = {
            "random_forest": Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ("clf", RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    class_weight="balanced",
                    random_state=42
                ))
            ]),
            "svm": Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ("clf", SVC(
                    kernel="rbf",
                    probability=True,
                    class_weight="balanced",
                    random_state=42
                ))
            ]),
            "gradient_boosting": Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ("clf", GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                ))
            ])
        }

    def train(self, texts: list[str], labels: list[str]) -> dict:
        """
        Entrena todos los modelos y retorna métricas comparativas.
        Usa cross-validation con k=5.
        Selecciona el mejor modelo por F1-score macro.
        """
        pass

    def predict(self, text: str) -> ClassificationResult:
        """
        Predice usando ensemble voting (soft voting).
        Retorna clase predicha + probabilidades.
        """
        pass

    def save(self, path: str) -> None:
        """Serializa modelos con joblib."""
        pass

    def load(self, path: str) -> None:
        """Carga modelos serializados."""
        pass
```

### 3.3 — Detector de Anomalías con TensorFlow/Keras (`backend/app/core/ml/anomaly_detector.py`)

```python
"""
Detector de anomalías en resultados de laboratorio usando Autoencoder.
Identifica valores de laboratorio anormales que podrían indicar riesgo.
"""

import tensorflow as tf
from tensorflow import keras
from keras import layers, Model

class LabAnomalyDetector:
    """Autoencoder para detección de anomalías en resultados de laboratorio."""

    def build_model(self, input_dim: int) -> Model:
        """
        Arquitectura del Autoencoder:

        Encoder:
          Input(input_dim) → Dense(64, relu) → BatchNorm → Dropout(0.3)
          → Dense(32, relu) → BatchNorm → Dropout(0.2)
          → Dense(16, relu)  ← latent space

        Decoder:
          Dense(16) → Dense(32, relu) → BatchNorm
          → Dense(64, relu) → BatchNorm
          → Dense(input_dim, sigmoid)

        Loss: MSE
        Optimizer: Adam(lr=1e-3)
        """
        pass

    def train(self, normal_data: np.ndarray, epochs: int = 100, batch_size: int = 32):
        """
        Entrena SOLO con datos normales.
        Usa EarlyStopping y ReduceLROnPlateau callbacks.
        Calcula threshold como percentil 95 del reconstruction error en training.
        """
        pass

    def detect_anomalies(self, lab_results: np.ndarray) -> list[AnomalyResult]:
        """
        Detecta anomalías.
        Reconstruye input, calcula MSE por muestra.
        Si MSE > threshold → anomalía.
        Retorna score de anomalía y features más anómalas.
        """
        pass

    def save(self, path: str) -> None:
        """Guarda modelo Keras + threshold."""
        pass
```

### 3.4 — Clustering de Riesgo (`backend/app/core/ml/risk_clusterer.py`)

```python
"""
Clustering no supervisado de pacientes por perfil de riesgo.
Agrupa pacientes similares para identificar poblaciones en riesgo.
"""

from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

class RiskClusterer:
    """Clustering de pacientes por perfil de riesgo."""

    def find_optimal_clusters(self, features: np.ndarray, max_k: int = 10) -> int:
        """
        Encuentra K óptimo usando:
        1. Método del codo (inertia)
        2. Silhouette score
        Retorna K óptimo.
        """
        pass

    def fit_kmeans(self, features: np.ndarray, n_clusters: int = None) -> dict:
        """
        Ajusta K-Means.
        Si n_clusters es None, usa find_optimal_clusters.
        Retorna: labels, centroids, silhouette_score, cluster_descriptions.
        """
        pass

    def fit_dbscan(self, features: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> dict:
        """
        Ajusta DBSCAN para encontrar clusters de forma natural.
        Identifica outliers (label = -1) como casos especiales de riesgo.
        """
        pass

    def describe_clusters(self, features: np.ndarray, labels: np.ndarray,
                          feature_names: list[str]) -> list[ClusterDescription]:
        """
        Genera descripción interpretable de cada cluster:
        - Centroide (valores promedio de cada feature)
        - Features más distintivas
        - Nivel de riesgo estimado (bajo/medio/alto/crítico)
        - Tamaño del cluster
        """
        pass

    def visualize_clusters(self, features: np.ndarray, labels: np.ndarray) -> str:
        """
        Genera visualización PCA 2D de clusters.
        Retorna path a imagen PNG guardada.
        """
        pass
```

### 3.5 — Transformer Classifier con PyTorch (`backend/app/core/ml/transformer_classifier.py`)

```python
"""
Clasificador de documentos usando PyTorch con Transformer fine-tuned.
Modelo más avanzado que el de HuggingFace, con custom training loop.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModel, AutoTokenizer

class MedicalDocDataset(Dataset):
    """Dataset custom para documentos médicos."""
    pass

class TransformerDocClassifier(nn.Module):
    """
    Arquitectura:
    BERT/RoBERTa encoder → Mean pooling → Dropout(0.3)
    → Linear(768, 256) → ReLU → Dropout(0.2)
    → Linear(256, num_classes)
    """
    pass

class TransformerTrainer:
    """Custom training loop con métricas detalladas."""

    def train(self, train_loader, val_loader, epochs=10, lr=2e-5):
        """
        Training loop con:
        - AdamW optimizer con weight decay
        - Linear warmup + cosine annealing scheduler
        - Gradient clipping (max_norm=1.0)
        - Early stopping en val F1
        - Logging de loss, accuracy, F1 por epoch
        - Guardado del mejor modelo
        """
        pass

    def evaluate(self, dataloader) -> dict:
        """
        Evaluación completa:
        - Accuracy, Precision, Recall, F1 (macro y per-class)
        - Confusion matrix
        - Classification report
        """
        pass
```

### 3.6 — Tests ML

```python
# test_classifier.py (Sklearn)
# - test_train_with_synthetic_data: entrena sin error, accuracy > 0.7
# - test_predict_returns_valid_result: resultado tiene clase y probabilidades
# - test_save_load_preserves_model: modelo guardado y cargado produce mismos resultados
# - test_cross_validation_scores: CV scores son razonables (>0.6)

# test_anomaly_detector.py (TF/Keras)
# - test_build_model_architecture: modelo tiene capas correctas
# - test_train_on_normal_data: entrena sin error, loss converge
# - test_detect_anomaly_on_outlier: valor extremo se detecta como anomalía
# - test_normal_data_not_flagged: datos normales no generan alertas

# test_risk_clusterer.py (Sklearn)
# - test_find_optimal_clusters: retorna K razonable (2-10)
# - test_kmeans_assigns_labels: todos los datos tienen label
# - test_dbscan_finds_outliers: datos extremos son outliers
# - test_cluster_descriptions_interpretable: descripciones tienen sentido
```

### 3.7 — Commit fase 3

```bash
git checkout -b feature/DSM-003-ml-module
git commit -m "feat(ml): implement supervised classifiers, TF anomaly detector, and risk clustering"
git tag v0.4.0
```

---

## FASE 4: MÓDULO RAG Y LLMs

> **Objetivo:** Permitir consultas en lenguaje natural sobre expedientes.
> **Tecnologías:** OpenAI API, Anthropic Claude, LangChain, Supabase pgvector

### 4.1 — Embedder (`backend/app/core/rag/embedder.py`)

```python
"""Generación de embeddings para chunks de documentos."""

from openai import OpenAI

class DocumentEmbedder:
    """Genera embeddings usando OpenAI text-embedding-3-small."""

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """
        Divide texto en chunks con overlap.
        Respeta límites de oraciones (no cortar a mitad de oración).
        """
        pass

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Genera embeddings batch.
        Maneja rate limiting con retry exponential backoff.
        Dimensión: 1536 (text-embedding-3-small).
        """
        pass

    def embed_and_store(self, document_id: str, text: str) -> int:
        """
        Chunka, embebe, y almacena en Supabase pgvector.
        Retorna número de chunks almacenados.
        """
        pass
```

### 4.2 — Vector Store (`backend/app/core/rag/vector_store.py`)

```python
"""Interface con Supabase pgvector para búsqueda semántica."""

class VectorStore:
    """Almacenamiento y búsqueda vectorial con Supabase pgvector."""

    def store_embeddings(self, document_id: str, chunks: list[str],
                         embeddings: list[list[float]]) -> None:
        """Almacena chunks con sus embeddings en pgvector."""
        pass

    def similarity_search(self, query_embedding: list[float],
                          top_k: int = 5, threshold: float = 0.7,
                          filter_patient_id: str = None) -> list[SearchResult]:
        """
        Búsqueda por similitud coseno.
        Filtra opcionalmente por patient_id.
        Retorna top_k resultados sobre threshold de similitud.
        """
        pass

    def hybrid_search(self, query: str, query_embedding: list[float],
                      top_k: int = 5) -> list[SearchResult]:
        """
        Búsqueda híbrida: combina vector similarity + full-text search.
        Usa RRF (Reciprocal Rank Fusion) para combinar rankings.
        """
        pass
```

### 4.3 — RAG Chain (`backend/app/core/rag/chain.py`)

```python
"""Pipeline RAG completo: Query → Retrieval → Generation."""

class RAGChain:
    """Cadena RAG para consultas sobre expedientes clínicos."""

    SYSTEM_PROMPT = """
    Eres un asistente médico AI de DocSalud MX. Tu rol es ayudar al personal
    de salud a consultar información de expedientes clínicos de pacientes.

    REGLAS ESTRICTAS:
    1. SOLO responde basándote en los documentos proporcionados como contexto.
    2. Si la información no está en el contexto, di "No encontré esa información
       en los expedientes disponibles."
    3. Cita el tipo de documento y fecha cuando sea posible.
    4. NUNCA inventes datos médicos, diagnósticos o resultados.
    5. Si detectas información preocupante (valores críticos, interacciones
       peligrosas), menciónalo explícitamente.
    6. Responde en español, con terminología médica apropiada.
    7. Protege la privacidad: no reveles información a usuarios no autorizados.
    """

    def query(self, question: str, patient_id: str = None) -> RAGResponse:
        """
        Pipeline completo:
        1. Embebe la pregunta
        2. Busca documentos relevantes (similarity_search)
        3. Construye prompt con contexto
        4. Llama al LLM (OpenAI GPT-4 o Claude)
        5. Parsea y estructura respuesta
        6. Retorna respuesta + fuentes citadas
        """
        pass

    def _build_prompt(self, question: str, context_chunks: list[SearchResult]) -> str:
        """Construye prompt con contexto recuperado."""
        pass

    def _call_llm(self, prompt: str, provider: str = "openai") -> str:
        """
        Llama al LLM seleccionado.
        Soporta: openai (GPT-4), anthropic (Claude).
        Fallback automático si uno falla.
        """
        pass
```

### 4.4 — Prompts Templates (`backend/app/core/rag/prompts.py`)

```python
"""Templates de prompts optimizados para diferentes tipos de consultas."""

QUERY_TEMPLATES = {
    "historial_general": """
        Basándote en los siguientes documentos del expediente del paciente,
        proporciona un resumen del historial clínico.

        Documentos:
        {context}

        Incluye: diagnósticos, medicamentos actuales, últimos resultados
        de laboratorio, y cualquier alerta importante.
    """,

    "medicamentos_actuales": """
        Basándote en las recetas más recientes del paciente, lista todos
        los medicamentos actuales con su dosis y frecuencia.

        Documentos:
        {context}

        Formato: Medicamento - Dosis - Frecuencia - Indicación
    """,

    "tendencia_laboratorio": """
        Analiza la tendencia de los resultados de laboratorio del paciente
        a lo largo del tiempo.

        Documentos:
        {context}

        Identifica: valores fuera de rango, tendencias preocupantes,
        y recomendaciones de seguimiento.
    """,

    "alertas_riesgo": """
        Revisa toda la información disponible del paciente e identifica
        cualquier factor de riesgo o situación que requiera atención.

        Documentos:
        {context}

        Considera: valores de laboratorio fuera de rango, interacciones
        medicamentosas, falta de seguimiento, condiciones no controladas.
    """
}
```

### 4.5 — Commit fase 4

```bash
git checkout -b feature/DSM-004-rag-module
git commit -m "feat(rag): implement embedding pipeline, vector store, and RAG chain with LLM integration"
git tag v0.5.0
```

---

## FASE 5: API Y MICROSERVICIOS

> **Objetivo:** Exponer toda la funcionalidad como API REST con FastAPI.
> **Tecnologías:** FastAPI, Pydantic, SQLAlchemy, asyncpg

### 5.1 — Entry Point (`backend/app/main.py`)

```python
"""
DocSalud MX — API Principal
FastAPI application con middleware, routers, y lifecycle management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
    - Inicializar conexión a DB
    - Cargar modelos ML en memoria
    - Inicializar cliente de embeddings
    - Verificar conexión a Supabase
    - Descargar modelos SpaCy si no existen

    Shutdown:
    - Cerrar pool de conexiones DB
    - Liberar memoria de modelos
    """
    pass

app = FastAPI(
    title="DocSalud MX API",
    description="Sistema de Digitalización Inteligente de Expedientes Clínicos",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)
```

### 5.2 — Endpoints detallados

**POST /api/v1/upload**
```python
"""
Recibe imagen o PDF de expediente clínico.

Request: multipart/form-data
  - file: UploadFile (image/jpeg, image/png, application/pdf)
  - patient_id: Optional[str]

Response: 202 Accepted
  {
    "document_id": "uuid",
    "status": "processing",
    "message": "Documento recibido, procesamiento iniciado"
  }

Pipeline interno:
1. Validar archivo (tipo, tamaño max 10MB)
2. Guardar en storage (S3 o local)
3. Ejecutar OCR async
4. Ejecutar NLP extraction async
5. Clasificar documento async
6. Generar embeddings async
7. Evaluar alertas async
8. Actualizar status a "completed"
"""
```

**GET /api/v1/patients/{patient_id}/documents**
```python
"""
Lista documentos procesados de un paciente.

Query params:
  - doc_type: Optional[str] — filtrar por tipo
  - date_from: Optional[date]
  - date_to: Optional[date]
  - page: int = 1
  - page_size: int = 20

Response: 200 OK
  {
    "items": [DocumentResponse],
    "total": int,
    "page": int,
    "pages": int
  }
"""
```

**POST /api/v1/query**
```python
"""
Consulta en lenguaje natural sobre expedientes.

Request:
  {
    "question": "¿Cuáles son los últimos resultados de glucosa del paciente?",
    "patient_id": "uuid" (opcional, si no se da busca en todos),
    "query_type": "general" | "medicamentos" | "laboratorio" | "alertas"
  }

Response: 200 OK
  {
    "answer": "Los últimos resultados de glucosa del paciente...",
    "sources": [
      {"document_id": "uuid", "document_type": "laboratorio", "date": "2024-01-15", "relevance": 0.92}
    ],
    "confidence": 0.87
  }
"""
```

**GET /api/v1/alerts**
```python
"""
Obtiene alertas activas.

Query params:
  - patient_id: Optional[str]
  - severity: Optional[str] — low, medium, high, critical
  - is_resolved: bool = false

Response: 200 OK
  {
    "alerts": [AlertResponse],
    "summary": {
      "total": 15,
      "critical": 2,
      "high": 5,
      "medium": 6,
      "low": 2
    }
  }
"""
```

**POST /api/v1/classify**
```python
"""
Clasifica un texto de documento.

Request:
  {"text": "Rx: Metformina 850mg..."}

Response: 200 OK
  {
    "document_type": "receta",
    "confidence": 0.94,
    "all_probabilities": {"receta": 0.94, "laboratorio": 0.03, ...},
    "model_used": "transformer"  // o "sklearn" si transformer no disponible
  }
"""
```

**GET /api/v1/search**
```python
"""
Búsqueda semántica sobre documentos.

Query params:
  - q: str — query de búsqueda
  - patient_id: Optional[str]
  - top_k: int = 5

Response: 200 OK
  {
    "results": [
      {
        "document_id": "uuid",
        "chunk_text": "...",
        "similarity_score": 0.89,
        "document_type": "laboratorio",
        "patient_name": "...",
        "date": "2024-01-15"
      }
    ]
  }
"""
```

**GET /api/v1/health**
```python
"""
Healthcheck del sistema.

Response: 200 OK
  {
    "status": "healthy",
    "components": {
      "database": "up",
      "vector_store": "up",
      "ocr_engine": "up",
      "ml_models": "loaded",
      "llm_api": "reachable"
    },
    "version": "1.0.0",
    "uptime_seconds": 3600
  }
"""
```

### 5.3 — Document Service (Orquestador)

```python
"""
Servicio que orquesta el pipeline completo de procesamiento de documentos.
"""

class DocumentService:
    """Orquesta OCR → NLP → ML → RAG para cada documento."""

    async def process_document(self, file_path: str, patient_id: str = None) -> Document:
        """
        Pipeline completo:
        1. OCR: extraer texto
        2. NLP: limpiar texto, extraer entidades, clasificar documento
        3. ML: clasificar con Sklearn como validación
        4. RAG: generar embeddings y almacenar
        5. Alertas: evaluar si hay condiciones de alerta
        6. DB: guardar todo en PostgreSQL
        7. Retornar documento procesado

        Cada paso tiene timeout y fallback.
        Si OCR falla → retornar error descriptivo
        Si NLP falla parcialmente → retornar lo que se pudo extraer
        Si ML falla → usar clasificación NLP como fallback
        """
        pass
```

### 5.4 — Commit fase 5

```bash
git checkout -b feature/DSM-005-api-microservices
git commit -m "feat(api): implement FastAPI endpoints, document processing pipeline, and service layer"
git tag v0.6.0
```

---

## FASE 6: FRONTEND REACT DASHBOARD

> **Objetivo:** Interfaz visual para upload, consulta y monitoreo.
> **Tecnologías:** React 18, TypeScript, Tailwind CSS, Recharts, React Query

### 6.1 — Componentes principales que Claude Code debe crear:

**DocumentUploader.tsx**
- Drag & drop zone (react-dropzone)
- Preview de imagen antes de subir
- Captura desde cámara (para celular)
- Progress bar durante procesamiento
- Resultado: texto extraído, tipo clasificado, entidades detectadas

**Dashboard (StatsCards + AlertsPanel + RiskChart)**
- Cards: Total pacientes, Documentos procesados hoy, Alertas activas, Score promedio de riesgo
- AlertsPanel: Lista de alertas ordenadas por severity con colores
- RiskChart: Gráfico de distribución de clusters de riesgo (Recharts PieChart)
- RecentDocuments: Últimos documentos procesados con status

**PatientDetail.tsx**
- Timeline de documentos del paciente
- Datos extraídos de cada documento
- Gráficos de tendencia de laboratorios (LineChart)
- Alertas activas del paciente
- Score de riesgo con indicador visual

**ChatInterface.tsx**
- Input de texto para consulta en lenguaje natural
- Burbujas de chat (usuario/AI)
- Fuentes citadas debajo de cada respuesta
- Sugerencias de queries comunes
- Indicador de confianza en la respuesta

### 6.2 — Paleta de colores y diseño

```
Primario:     #0F766E (teal-700) — Confianza médica
Secundario:   #1E40AF (blue-800) — Profesional
Acento:       #F59E0B (amber-500) — Alertas medias
Peligro:      #DC2626 (red-600) — Alertas críticas
Éxito:        #16A34A (green-600) — Confirmación
Background:   #F8FAFC (slate-50) — Limpio
Cards:        #FFFFFF con sombra sutil
```

### 6.3 — Commit fase 6

```bash
git checkout -b feature/DSM-006-frontend-dashboard
git commit -m "feat(frontend): implement React dashboard with upload, patient view, chat, and alerts"
git tag v0.7.0
```

---

## FASE 7: DEVOPS, DOCKER Y CI/CD

> **Objetivo:** Containerización completa y pipeline de CI/CD.
> **Tecnologías:** Docker, Docker Compose, GitHub Actions, NGINX

### 7.1 — docker-compose.prod.yml

```yaml
# Claude Code debe crear docker-compose de producción:
# - Backend: multi-stage build (builder + runner), non-root user, healthcheck
# - Frontend: build estático + NGINX para servir
# - PostgreSQL: con pgvector, volumen persistente, backup automático
# - Redis: con volumen persistente
# - NGINX: reverse proxy, SSL termination, rate limiting
# - Network: bridge privada entre servicios
# - Restart policies: unless-stopped para todos
```

### 7.2 — GitHub Actions CI (`/.github/workflows/ci.yml`)

```yaml
# Trigger: push a develop o PR a develop/main
#
# Jobs:
# 1. lint:
#    - Black formatting check
#    - Ruff linting
#    - mypy type checking
#    - ESLint (frontend)
#
# 2. test-backend:
#    - Setup PostgreSQL service container
#    - Install dependencies
#    - Run pytest with coverage (min 70%)
#    - Upload coverage report
#
# 3. test-frontend:
#    - Install dependencies
#    - Run vitest
#    - Upload coverage report
#
# 4. security:
#    - pip-audit para vulnerabilidades Python
#    - npm audit para vulnerabilidades Node
#
# 5. build:
#    - Build Docker images
#    - Verificar que containers inician correctamente
```

### 7.3 — GitHub Actions CD (`/.github/workflows/cd.yml`)

```yaml
# Trigger: push a main (merge de release branch)
#
# Jobs:
# 1. deploy:
#    - SSH al servidor AWS EC2
#    - Pull última imagen
#    - docker-compose down
#    - docker-compose up -d
#    - Healthcheck post-deploy
#    - Notificar (opcional: Slack/Discord)
```

### 7.4 — Makefile

```makefile
# Comandos que Claude Code debe implementar:
# make setup        — Instala dependencias, crea .env, descarga modelos
# make dev          — Levanta docker-compose dev con hot-reload
# make test         — Corre todos los tests
# make test-unit    — Solo tests unitarios
# make test-integration — Solo tests de integración
# make lint         — Corre todos los linters
# make format       — Formatea código (Black, isort)
# make docker-build — Build de imágenes Docker
# make docker-up    — Levanta producción local
# make docker-down  — Baja todos los containers
# make migrate      — Ejecuta migraciones de DB
# make seed         — Seed de datos iniciales
# make train-ner    — Entrena modelo NER
# make train-classifier — Entrena clasificador
# make generate-data — Genera datos sintéticos
# make clean        — Limpia artefactos (pycache, node_modules, etc.)
```

### 7.5 — Commit fase 7

```bash
git checkout -b feature/DSM-007-devops
git commit -m "feat(devops): add Docker production config, CI/CD pipelines, NGINX, and Makefile"
git tag v0.8.0
```

---

## FASE 8: DEPLOY EN AWS

> **Objetivo:** Desplegar en AWS EC2 con infraestructura robusta.
> **Tecnologías:** AWS EC2, S3, Route 53, ACM (SSL)

### 8.1 — Setup del servidor

```bash
# Script que Claude Code debe crear (infrastructure/scripts/setup-server.sh):
# 1. Update system packages
# 2. Install Docker + Docker Compose
# 3. Install NGINX
# 4. Configure firewall (UFW): only 22, 80, 443
# 5. Setup swap (2GB para servidor pequeño)
# 6. Configure log rotation
# 7. Setup automatic security updates
# 8. Create non-root user 'docsalud'
# 9. Configure SSH key-only authentication
# 10. Install certbot for SSL
```

### 8.2 — NGINX config

```nginx
# Que Claude Code debe crear:
# - Reverse proxy a backend (port 8000)
# - Servir frontend estático
# - SSL con Let's Encrypt
# - Rate limiting: 10 req/s por IP
# - Gzip compression
# - Security headers (HSTS, X-Frame-Options, etc.)
# - Max body size: 10MB (para upload de documentos)
```

### 8.3 — Commit fase 8

```bash
git checkout -b feature/DSM-008-aws-deploy
git commit -m "feat(deploy): add AWS EC2 deployment scripts, NGINX config, and SSL setup"
git tag v0.9.0
```

---

## FASE 9: TESTING Y QA

### 9.1 — Estructura de tests

```
tests/
├── unit/              # Tests aislados de cada componente
│   ├── test_ocr_*     # Fase 1
│   ├── test_nlp_*     # Fase 2
│   ├── test_ml_*      # Fase 3
│   ├── test_rag_*     # Fase 4
│   └── test_api_*     # Fase 5
├── integration/       # Tests de componentes combinados
│   ├── test_upload_pipeline.py    # Upload → OCR → NLP → ML → Storage
│   ├── test_search_endpoint.py    # Query → Embedding → Search → Response
│   └── test_alert_generation.py   # Document → Analysis → Alert
└── e2e/               # Tests end-to-end
    └── test_full_pipeline.py      # Documento completo de inicio a fin
```

### 9.2 — Coverage mínimo requerido
- **Unit tests:** 80% coverage
- **Integration tests:** Todos los endpoints con happy path y error path
- **E2E:** Al menos 3 escenarios completos (receta, laboratorio, nota médica)

### 9.3 — Commit fase 9

```bash
git checkout -b feature/DSM-009-testing
git commit -m "test: comprehensive test suite with unit, integration, and e2e tests"
git tag v0.9.5
```

---

## FASE 10: DOCUMENTACIÓN Y PORTFOLIO

### 10.1 — README.md robusto

```markdown
# Claude Code debe crear un README con:
# - Badges (CI status, coverage, Python version, license)
# - Logo/banner del proyecto
# - Descripción clara del problema e impacto social
# - Screenshots del dashboard
# - Arquitectura (diagrama Mermaid)
# - Quick start (3 comandos: clone, setup, run)
# - Documentación de API (link a /docs)
# - Stack tecnológico con badges
# - Estructura del proyecto
# - Cómo contribuir
# - Model cards (resumen de cada modelo ML)
# - Performance metrics
# - Roadmap futuro
# - Licencia y créditos
```

### 10.2 — Model Cards (docs/model-cards/)

Cada modelo ML debe tener documentación:
- Nombre y versión
- Tipo de modelo y arquitectura
- Dataset de entrenamiento (tamaño, distribución)
- Métricas de evaluación (accuracy, F1, precision, recall)
- Limitaciones conocidas
- Uso ético y consideraciones de sesgo
- Instrucciones de reproducción

### 10.3 — Commit final

```bash
git checkout develop
git checkout -b release/v1.0.0
# Últimos ajustes
git checkout main
git merge release/v1.0.0
git tag v1.0.0
git push origin main --tags
```

---

## PROMPTS EXACTOS PARA CLAUDE CODE

### Prompt de inicio de sesión (usar siempre al abrir Claude Code):

```
Lee el archivo CLAUDE.md en la raíz del proyecto. Este es tu fuente de verdad.
Estamos trabajando en DocSalud MX. Confirma qué fase estamos y qué sigue.
```

### Prompts por fase:

**FASE 0:**
```
Ejecuta la Fase 0 del CLAUDE.md. Crea toda la estructura de directorios,
.gitignore, .env.example, Makefile, docker-compose.yml con PostgreSQL+pgvector
y Redis, Dockerfile del backend con Tesseract instalado, y la migración inicial
de Alembic con el schema de base de datos definido en CLAUDE.md sección 0.3.
No olvides el README.md inicial con badges.
```

**FASE 1:**
```
Ejecuta la Fase 1 del CLAUDE.md. Implementa el módulo OCR completo:
1. ImagePreprocessor con todas las funciones de OpenCV (deskew, denoise,
   adaptive threshold, detect regions, perspective correction, CLAHE)
2. OCRExtractor con Tesseract + PyMuPDF (imagen y PDF)
3. Dataclasses OCRResult y TextBlock
4. Tests unitarios completos
5. Jupyter notebook de exploración (01_ocr_exploration.ipynb)
Sigue las convenciones de código del CLAUDE.md sección 4.
```

**FASE 2:**
```
Ejecuta la Fase 2 del CLAUDE.md. Implementa el módulo NLP completo:
1. generate_synthetic_data.py — genera 2000+ documentos médicos sintéticos
   con anotaciones NER en formato SpaCy
2. scraper.py — BeautifulSoup scraper del cuadro básico de medicamentos
3. TextCleaner con NLTK (fix OCR artifacts, normalize abbreviations, segment)
4. MedicalNERExtractor con SpaCy (train_custom_model + extract)
5. DocumentClassifier con HuggingFace Transformers (fine-tune + classify)
6. Tests unitarios completos
Sigue las convenciones del CLAUDE.md.
```

**FASE 3:**
```
Ejecuta la Fase 3 del CLAUDE.md. Implementa el módulo ML completo:
1. FeatureEngineer — TF-IDF + features de paciente + features de lab
2. SklearnDocumentClassifier — Random Forest + SVM + GradientBoosting ensemble
3. LabAnomalyDetector — Autoencoder TF/Keras para detección de anomalías
4. RiskClusterer — K-Means + DBSCAN con visualización PCA
5. TransformerDocClassifier — PyTorch custom training loop
6. model_registry.py — Carga y versionado de modelos
7. Tests unitarios para cada componente
8. Notebooks de entrenamiento y evaluación
```

**FASE 4:**
```
Ejecuta la Fase 4 del CLAUDE.md. Implementa el módulo RAG:
1. DocumentEmbedder — chunking + OpenAI embeddings
2. VectorStore — Supabase pgvector con similarity y hybrid search
3. RAGChain — pipeline completo con system prompt médico
4. prompts.py — templates para diferentes tipos de consulta
5. Tests con mocks de APIs
```

**FASE 5:**
```
Ejecuta la Fase 5 del CLAUDE.md. Implementa la API completa:
1. FastAPI app con lifespan, middleware (CORS, logging, rate limit)
2. Todos los endpoints: upload, patients, documents, search, query, alerts, classify, health
3. Pydantic schemas para request/response
4. DocumentService como orquestador del pipeline
5. Repository pattern para acceso a DB
6. Tests de integración para cada endpoint
```

**FASE 6:**
```
Ejecuta la Fase 6 del CLAUDE.md. Implementa el frontend React:
1. Setup Vite + React 18 + TypeScript + Tailwind
2. Layout: Header + Sidebar + MainLayout
3. DocumentUploader con drag & drop y camera capture
4. Dashboard con StatsCards, AlertsPanel, RiskChart (Recharts)
5. PatientDetail con timeline y gráficos de laboratorio
6. ChatInterface con burbujas, fuentes citadas, y sugerencias
7. API service layer con Axios + React Query
8. Paleta de colores médica profesional definida en CLAUDE.md
```

**FASE 7:**
```
Ejecuta la Fase 7 del CLAUDE.md. Implementa DevOps:
1. docker-compose.prod.yml con multi-stage builds
2. NGINX reverse proxy config con SSL y rate limiting
3. GitHub Actions CI (lint, test, security, build)
4. GitHub Actions CD (deploy a AWS)
5. Makefile con todos los comandos
6. pre-commit hooks
```

**FASE 8:**
```
Ejecuta la Fase 8 del CLAUDE.md. Implementa deploy:
1. setup-server.sh para configurar EC2
2. deploy.sh con zero-downtime deployment
3. backup.sh para PostgreSQL
4. NGINX config con SSL (Let's Encrypt)
5. Monitoreo básico con healthchecks
```

**FASE 9:**
```
Ejecuta la Fase 9 del CLAUDE.md. Completa testing:
1. Asegurar 80% coverage en unit tests
2. Integration tests para todos los endpoints
3. E2E tests: receta, laboratorio, nota médica
4. Generar reporte de coverage
```

**FASE 10:**
```
Ejecuta la Fase 10 del CLAUDE.md. Documentación final:
1. README.md completo con badges, screenshots, arquitectura Mermaid
2. Model cards para cada modelo ML
3. API docs (FastAPI genera automático en /docs)
4. Deployment guide
5. Sprint retrospectives
6. CHANGELOG.md
```

---

## TROUBLESHOOTING

### Errores comunes y soluciones:

**Tesseract no encuentra idioma español:**
```bash
apt-get install tesseract-ocr-spa
# Verificar: tesseract --list-langs | grep spa
```

**SpaCy modelo no encontrado:**
```bash
python -m spacy download es_core_news_lg
```

**NLTK data no encontrada:**
```python
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
```

**pgvector no disponible en PostgreSQL:**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**OpenCV headless vs full:**
```bash
# Usar headless para servidor (sin GUI)
pip install opencv-python-headless
# No instalar opencv-python Y opencv-python-headless juntos
```

**CUDA/GPU no disponible para PyTorch:**
```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Los modelos deben funcionar en CPU también (más lento pero funcional)
```

**Rate limiting de OpenAI API:**
```python
# Usar tenacity para retry con backoff exponencial
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def call_openai(...):
    pass
```

**Docker build tarda mucho:**
```dockerfile
# Cachear capas de dependencias antes de copiar código
COPY requirements.txt .
RUN pip install -r requirements.txt
# LUEGO copiar código (cambios frecuentes)
COPY . .
```

---

## NOTAS FINALES PARA CLAUDE CODE

1. **SIEMPRE** lee este archivo antes de empezar cualquier tarea
2. **SIEMPRE** crea tests antes o junto con la implementación
3. **SIEMPRE** usa type hints y docstrings en Python
4. **SIEMPRE** haz commits semánticos después de cada módulo funcional
5. **NUNCA** hardcodees API keys o secrets — usa .env
6. **NUNCA** comitees datos de pacientes reales — solo sintéticos
7. **NUNCA** ignores errores silenciosamente
8. **NUNCA** uses `print()` — usa `structlog` logger
9. El código debe funcionar en CPU (GPU es bonus, no requisito)
10. Prioriza claridad sobre cleverness — este es código de producción médica

---

*Última actualización: Febrero 2026*
*Versión del pipeline: 1.0.0*
