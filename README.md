# DocSalud MX

[![CI](https://github.com/saidmoreno/docsalud-mx/actions/workflows/ci.yml/badge.svg)](https://github.com/saidmoreno/docsalud-mx/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Sistema de Digitalizacion Inteligente de Expedientes Clinicos**

---

## Problema

En Mexico, miles de clinicas rurales manejan expedientes medicos en papel. Esto causa perdida de historiales clinicos, imposibilidad de seguimiento a enfermedades cronicas, diagnosticos duplicados y dificultad para referencias entre niveles de atencion.

## Solucion

DocSalud MX es un sistema de AI que:

1. **Recibe** fotografias o escaneos de expedientes clinicos en papel
2. **Digitaliza** el contenido mediante OCR + vision artificial (OpenCV, Tesseract)
3. **Extrae** informacion estructurada con NLP (SpaCy, HuggingFace)
4. **Clasifica** documentos automaticamente con ML (supervisado + no supervisado)
5. **Genera alertas** de pacientes en riesgo
6. **Permite consultas** en lenguaje natural sobre historiales (RAG + LLMs)

## Arquitectura

```
Frontend (React) --> API Gateway (FastAPI) --> OCR Module (OpenCV + Tesseract)
                                          --> NLP Module (SpaCy + HuggingFace)
                                          --> ML Module (Sklearn + PyTorch + TF)
                                          --> RAG Engine (LLM + pgvector)
                                                    |
                                              Data Layer
                                    (PostgreSQL + pgvector + Redis)
```

## Stack Tecnologico

| Capa | Tecnologias |
|------|-------------|
| **OCR / Vision** | OpenCV, Tesseract, PyMuPDF, Pillow |
| **NLP** | SpaCy, NLTK, HuggingFace Transformers, BeautifulSoup |
| **ML** | Scikit-learn, PyTorch, TensorFlow/Keras, XGBoost |
| **RAG / LLMs** | OpenAI, Anthropic Claude, LangChain, pgvector |
| **API** | FastAPI, Pydantic, SQLAlchemy, asyncpg |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Recharts |
| **Infra** | Docker, GitHub Actions, NGINX, AWS EC2 |
| **DB** | PostgreSQL 16 + pgvector, Redis 7 |

## Quick Start

```bash
# 1. Clonar el repositorio
git clone https://github.com/saidmoreno/docsalud-mx.git
cd docsalud-mx

# 2. Configurar entorno
make setup

# 3. Levantar con Docker
make dev
```

La API estara disponible en `http://localhost:8000/docs` y el frontend en `http://localhost:5173`.

## Estructura del Proyecto

```
docsalud-mx/
├── backend/           # FastAPI + modulos AI/ML
│   ├── app/
│   │   ├── api/       # Endpoints REST
│   │   ├── core/      # OCR, NLP, ML, RAG modules
│   │   ├── db/        # SQLAlchemy models + Alembic
│   │   └── services/  # Business logic
│   ├── models/        # Modelos ML entrenados
│   ├── data/          # Datos de entrenamiento
│   ├── notebooks/     # Jupyter notebooks
│   └── tests/         # Unit, integration, e2e
├── frontend/          # React + TypeScript + Tailwind
├── infrastructure/    # Docker, NGINX, Terraform
└── docs/              # Documentacion y model cards
```

## Comandos Utiles

```bash
make help              # Ver todos los comandos disponibles
make dev               # Desarrollo con hot-reload
make test              # Ejecutar tests
make lint              # Verificar estilo de codigo
make format            # Formatear codigo
make generate-data     # Generar datos sinteticos
make train-ner         # Entrenar modelo NER
```

## API Docs

Con el servidor corriendo, visita:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Licencia

[MIT](./LICENSE) - Said Ivan Briones Moreno, 2026.
