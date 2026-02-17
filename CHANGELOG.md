# Changelog

Todos los cambios notables a este proyecto seran documentados en este archivo.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-02-17

### Added
- Documentacion completa (README, model cards, deployment guide, sprint retrospectives, CHANGELOG)
- Guia rapida de deploy AWS (`AWS_DEPLOY.md` y `PASOS_FINALES.md`)
- Model cards para los 4 modelos ML principales
- 4 Sprint retrospectives documentando el proceso de desarrollo

### Fixed
- Corregido permisos del directorio `/app/uploads/` en Dockerfile.prod
- Actualizado `libgl1-mesa-glx` a `libgl1` para compatibilidad con Debian Trixie
- Workers de Uvicorn reducidos de 4 a 2 para instancias t3.small

---

## [0.9.0] - 2026-02-15 (v0.9.0 — DSM-008)

### Added
- Scripts de deploy en AWS EC2 (`infrastructure/scripts/deploy.sh`)
- Script de inicializacion de SSL con Let's Encrypt (`infrastructure/scripts/ssl-init.sh`)
- Script de healthcheck completo (`infrastructure/scripts/healthcheck.sh`)
- Script de backup de PostgreSQL (`infrastructure/scripts/backup.sh`)
- Script de restauracion de DB (`infrastructure/scripts/restore-db.sh`)
- Documentacion detallada de deploy en AWS (`docs/deployment-guide.md`)
- NGINX configurado para HTTPS con redireccion HTTP→HTTPS
- Soporte para auto-renovacion de certificados SSL via Certbot

### Changed
- NGINX actualizado a configuracion full HTTPS (puerto 443 con Let's Encrypt)
- Health endpoint actualizado con checks reales de Supabase y Groq API

---

## [0.8.0] - 2026-02-14 (v0.8.0 — DSM-007)

### Added
- `docker-compose.prod.yml` con configuracion de produccion completa
- `Dockerfile.prod` con multi-stage build (builder + runner) y usuario non-root
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`): lint, test, security, build
- GitHub Actions CD pipeline (`.github/workflows/cd.yml`): deploy automatico a AWS
- `Makefile` con todos los comandos del proyecto
- Configuracion NGINX como reverse proxy con rate limiting y compresion gzip
- Pre-commit hooks con black, ruff y mypy
- Servicio Certbot en docker-compose.prod.yml para SSL automatico

### Changed
- Backend reducido a 2 workers de Uvicorn para optimizar uso de memoria en t3.small
- Variables de entorno reorganizadas para separar dev/prod

---

## [0.7.0] - 2026-02-13 (v0.7.0 — DSM-006)

### Added
- Frontend React 18 + TypeScript + Tailwind CSS con Vite
- Componente `DocumentUploader` con drag & drop y preview de imagen
- Dashboard con `StatsCards`, `AlertsPanel`, `RiskChart` (Recharts PieChart)
- Vista de detalle de paciente `PatientDetail` con timeline y graficos de laboratorio
- `ChatInterface` para consultas en lenguaje natural con fuentes citadas
- Hooks personalizados: `useUpload`, `usePatients`, `useSearch`, `useChat`
- Servicio API con Axios + React Query para cache y estado del servidor
- Paleta de colores medica profesional (teal-700 primario, blue-800 secundario)

---

## [0.6.0] - 2026-02-12 (v0.6.0 — DSM-005)

### Added
- API FastAPI completa con 9 endpoints REST
- `POST /api/v1/upload` — pipeline completo de procesamiento de documentos
- `GET /api/v1/patients` y `GET /api/v1/patients/{id}` — CRUD de pacientes
- `GET /api/v1/patients/{id}/documents` — documentos por paciente
- `POST /api/v1/query` — consulta RAG en lenguaje natural
- `GET /api/v1/search` — busqueda semantica con pgvector
- `GET /api/v1/alerts` — alertas clinicas con filtros
- `POST /api/v1/classify` — clasificacion de documentos
- `GET /api/v1/health` — healthcheck de todos los componentes
- `DocumentService` como orquestador del pipeline OCR → NLP → ML → RAG
- `SearchService` con RAG completo usando Groq API
- `AlertService` para generacion y gestion de alertas clinicas
- Repository pattern para acceso a PostgreSQL (PatientRepo, DocumentRepo, AlertRepo)
- Pydantic schemas v2 para validacion de request/response
- Middleware de CORS, logging estructurado con structlog, y rate limiting
- Soporte para embeddings locales con `sentence-transformers/all-MiniLM-L6-v2` (384 dims)
- Integracion con Groq API (llama-3.3-70b-versatile) como LLM

### Changed
- Health endpoint cambiado de valores hardcoded a checks reales async
- Vector embeddings cambiados de 1536 dims (OpenAI) a 384 dims (sentence-transformers)

---

## [0.5.0] - 2026-02-11 (RAG — incluido en v0.6.0)

### Added
- `DocumentEmbedder` con chunking inteligente y embeddings via sentence-transformers
- `VectorStore` con interfaz a Supabase pgvector (similarity search + hybrid search)
- `RAGChain` con pipeline completo: query → retrieval → generation
- System prompt medico en espanol con restricciones anti-alucinacion
- Templates de prompts para diferentes tipos de consulta (`prompts.py`)
- Soporte para OpenAI y Anthropic Claude como LLMs alternativos

---

## [0.4.0] - 2026-02-10 (v0.4.0 — DSM-003)

### Added
- `SklearnDocumentClassifier`: ensemble de Random Forest + SVM + GradientBoosting
- `LabAnomalyDetector`: autoencoder denso con TensorFlow/Keras para deteccion de anomalias
- `RiskClusterer`: K-Means + DBSCAN para clustering de pacientes con visualizacion PCA
- `TransformerDocClassifier`: custom training loop PyTorch con BERT en espanol
- `FeatureEngineer`: pipeline de feature extraction (TF-IDF + features de paciente + lab)
- `ModelRegistry`: carga y versionado de modelos ML serializados
- Scripts de entrenamiento: `train_classifier.py`, `train_anomaly_detector.py`
- Notebooks Jupyter: `03_classifier_training.ipynb`, `04_clustering_analysis.ipynb`

---

## [0.3.0] - 2026-02-09 (v0.3.0 — DSM-002)

### Added
- `MedicalNERExtractor`: NER con SpaCy fine-tuned con 15 tipos de entidades medicas
- `TextCleaner`: limpieza de texto OCR con NLTK (fix artefactos, normalizacion, segmentacion)
- `DocumentClassifier`: clasificador con HuggingFace Transformers (RoBERTa biomedical)
- `MedicalReferenceScraper`: scraper BeautifulSoup para cuadro basico de medicamentos
- Script `generate_synthetic_data.py`: genera 3,000+ documentos medicos sinteticos
- Script `train_ner_model.py`: fine-tuning de SpaCy NER con anotaciones custom
- Notebook `02_ner_training.ipynb`: exploracion del entrenamiento NER
- Datos de referencia: `data/reference/cie10_codes.json`, `medications.json`, `lab_ranges.json`
- 15 tipos de entidades NER: MEDICAMENTO, DOSIS, DIAGNOSTICO, CODIGO_CIE10, SIGNO_VITAL, etc.
- Normalizacion de abreviaturas medicas mexicanas

---

## [0.2.0] - 2026-02-08 (v0.2.0 — DSM-001)

### Added
- `ImagePreprocessor`: pipeline OpenCV con deskew, denoise, adaptive threshold, CLAHE, perspective correction
- `OCRExtractor`: motor OCR con Tesseract (imagenes) y PyMuPDF (PDFs nativos/escaneados)
- `ImageHandler`: manejo y validacion de imagenes (JPG, PNG, WEBP)
- `PDFHandler`: manejo de PDFs con deteccion de contenido nativo vs escaneado
- Dataclasses `OCRResult` y `TextBlock` con texto, confianza y bounding boxes
- Tests unitarios OCR: 25 tests en `test_ocr_preprocessor.py`, 20 tests en `test_ocr_extractor.py`
- Notebook `01_ocr_exploration.ipynb`: exploracion del pipeline OCR

---

## [0.1.0] - 2026-02-07 (v0.1.0 — Setup inicial)

### Added
- Estructura completa de directorios del proyecto (backend, frontend, infrastructure, docs)
- `.gitignore` completo para Python, Node.js, Docker y datos sensibles
- `.env.example` con todas las variables documentadas
- `README.md` inicial con descripcion del proyecto
- `LICENSE` MIT
- `docker-compose.yml` para desarrollo local (PostgreSQL 16 + pgvector, Redis 7, Backend, Frontend)
- `Dockerfile` del backend con Tesseract OCR en espanol, SpaCy, NLTK, OpenCV
- Schema de base de datos PostgreSQL: patients, documents, extracted_entities, alerts, document_embeddings
- Migracion inicial de Alembic
- Archivos `__init__.py` en todos los modulos Python
- `CLAUDE.md`: fuente unica de verdad con el pipeline completo de desarrollo

---

[1.0.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v1.0.0
[0.9.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.9.0
[0.8.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.8.0
[0.7.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.7.0
[0.6.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.6.0
[0.4.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.4.0
[0.3.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.3.0
[0.2.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.2.0
[0.1.0]: https://github.com/saidbriones/docsalud-mx/releases/tag/v0.1.0
