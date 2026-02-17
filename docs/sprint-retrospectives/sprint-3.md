# Sprint 3 Retrospective — RAG, API y Frontend

**Sprint:** 3
**Periodo:** Febrero 2026, Semana 3
**Duracion:** 1 semana
**Equipo:** Said Ivan Briones Moreno (Solo Developer + AI Pair: Claude Code)

---

## Objetivo del Sprint

Implementar el motor RAG con LLMs (Fase 4), la API FastAPI completa (Fase 5) y el Frontend React (Fase 6).

---

## User Stories Completadas

| ID | Historia | Puntos | Estado |
|----|----------|--------|--------|
| DSM-009 | Como medico, quiero hacer preguntas en lenguaje natural sobre el expediente de un paciente | 13 | Completado |
| DSM-010 | Como medico, quiero buscar documentos por contenido semantico | 8 | Completado |
| DSM-011 | Como desarrollador, quiero una API REST completa con todos los endpoints documentados | 13 | Completado |
| DSM-012 | Como medico, quiero un dashboard visual para ver pacientes, documentos y alertas | 13 | Completado |
| DSM-013 | Como medico, quiero subir documentos desde el navegador con drag & drop | 5 | Completado |

**Total puntos completados:** 52/52 (100%)

---

## Lo Que Salio Bien

1. **RAG con Groq API:** La decision de usar Groq (llama-3.3-70b) en lugar de OpenAI para el MVP fue excelente — gratuito, rapido (~1s de latencia) y de alta calidad en espanol.

2. **sentence-transformers local:** Usar `all-MiniLM-L6-v2` para embeddings locales elimina costos de API y reduce latencia. 384 dimensiones son suficientes para documentos medicos.

3. **FastAPI async:** La arquitectura async de FastAPI maneja bien la concurrencia en el pipeline OCR→NLP→ML que puede tardar 3-5 segundos.

4. **React Query:** La combinacion React Query + Zustand simplifica enormemente el manejo de estado del frontend sin boilerplate excesivo.

5. **Tailwind CSS:** El desarrollo del UI fue muy rapido con la paleta de colores medica preestablecida en CLAUDE.md.

6. **System prompt medico:** El prompt del asistente RAG en espanol con restricciones claras ("solo responde con el contexto disponible") reduce significativamente las alucinaciones.

---

## Lo Que Salio Mal

1. **pgvector 384 vs 1536:** El schema inicial tenia `vector(1536)` para OpenAI. Al cambiar a sentence-transformers (384 dims), hubo que recrear las tablas. Requirio SQL manual por bug en Alembic (server_default con comillas).

2. **CORS en produccion:** Las CORS origins en .env debieron configurarse desde el inicio para incluir el dominio de produccion.

3. **Upload de archivos grandes:** PDFs de mas de 5MB ocasionalmente time-out en el pipeline completo. Se optimizo con procesamiento async mas robusto.

4. **ChatInterface sin historial:** La primera version del chat no mantenia historial de conversacion. Se agrego estado local de mensajes.

5. **ReDoc vs Swagger:** La configuracion inicial solo habilitaba Swagger. Se agrego ReDoc para documentacion mas legible.

---

## Acciones de Mejora

| Accion | Responsable | Sprint |
|--------|-------------|--------|
| Agregar historial de conversacion persistente al RAG | Said | Backlog |
| Implementar paginacion en ChatInterface | Said | Backlog |
| Optimizar pipeline para PDFs >5MB con chunking | Said | Backlog |

---

## Metricas del Sprint

| Metrica | Valor |
|---------|-------|
| Story points completados | 52 |
| Endpoints de API implementados | 9 |
| Componentes React creados | 20 |
| Tests de integracion | 15 |
| Tiempo promedio de query RAG | ~1.8 segundos |
| Tiempo promedio de OCR | ~3.2 segundos (imagen tipica) |
| Bugs encontrados | 7 |
| Bugs resueltos | 7 |

---

## Commits del Sprint

- `feat(api): implement FastAPI endpoints, document processing pipeline, and service layer` (v0.6.0)
- `feat(frontend): implement React dashboard with upload, patient view, chat, and alerts` (v0.7.0)
- (RAG incluido en v0.6.0 como parte del pipeline de documentos)

---

## Decision Tecnica Destacada: Groq vs OpenAI

Durante este sprint se tomo la decision de usar **Groq API** en lugar de OpenAI para el MVP:

| Criterio | Groq (llama-3.3-70b) | OpenAI (gpt-4o) |
|----------|---------------------|-----------------|
| Costo | GRATIS (tier gratuito) | ~$5-15/1M tokens |
| Latencia | ~0.8s | ~2-4s |
| Calidad en espanol | Excelente | Excelente |
| Limite de requests | 30 RPM (gratuito) | Rate-limited por costo |
| Disponibilidad | Alta | Alta |

**Conclusion:** Para un MVP de demostracion, Groq ofrece mejor value. En produccion real se migraria a OpenAI o se usaria Claude API (Anthropic) para mayor control y SLAs garantizados.

---

*Sprint 3 completado: 14 Febrero 2026*
