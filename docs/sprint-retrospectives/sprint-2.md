# Sprint 2 Retrospective — NLP y Machine Learning

**Sprint:** 2
**Periodo:** Febrero 2026, Semana 2
**Duracion:** 1 semana
**Equipo:** Said Ivan Briones Moreno (Solo Developer + AI Pair: Claude Code)

---

## Objetivo del Sprint

Implementar los modulos NLP (Fase 2) y ML (Fase 3): extraccion de entidades medicas, clasificacion de documentos, deteccion de anomalias y clustering de riesgo.

---

## User Stories Completadas

| ID | Historia | Puntos | Estado |
|----|----------|--------|--------|
| DSM-004 | Como medico, quiero que el sistema identifique automaticamente medicamentos, dosis y diagnosticos del texto OCR | 13 | Completado |
| DSM-005 | Como administrador, quiero que los documentos se clasifiquen en receta/laboratorio/nota/referencia | 8 | Completado |
| DSM-006 | Como medico, quiero que el sistema detecte resultados de laboratorio anormales automaticamente | 8 | Completado |
| DSM-007 | Como director de clinica, quiero ver los pacientes agrupados por nivel de riesgo | 8 | Completado |
| DSM-008 | Como desarrollador, quiero datos sinteticos de entrenamiento para los modelos ML | 5 | Completado |

**Total puntos completados:** 42/42 (100%)

---

## Lo Que Salio Bien

1. **Datos sinteticos de alta calidad:** El script `generate_synthetic_data.py` genera documentos muy realistas con variaciones apropiadas (abreviaturas medicas, nombres tipicos mexicanos).

2. **SpaCy fine-tuning rapido:** El fine-tuning sobre `es_core_news_lg` converge en ~30 iteraciones con buenas metricas F1.

3. **Ensemble Sklearn:** La votacion suave (soft voting) del ensemble Random Forest + SVM + GradientBoosting supera a cualquier modelo individual.

4. **Autoencoder para anomalias:** El enfoque de entrenar solo con datos normales es muy potente — detecta patrones anomalos sin necesitar datos etiquetados de cada tipo de anomalia.

5. **Silhouette >0.65:** Los clusters de K-Means tienen buena separacion natural en el espacio de features de pacientes.

---

## Lo Que Salio Mal

1. **HuggingFace model grande:** `PlanTL-GOB-ES/roberta-base-biomedical-clinical-es` pesa ~500MB. El tiempo de descarga en la primera ejecucion es considerable. Se resolvio con cache de modelos en Docker volume.

2. **Dependencia de GPU para Transformer:** El fine-tuning del clasificador Transformer es significativamente mas lento en CPU (t3.small). Para el MVP se usa como fallback al Sklearn ensemble.

3. **Normalizacion de abreviaturas:** El diccionario inicial de abreviaturas medicas tenia ~50 entradas. En pruebas reales se encontraron ~20 abreviaturas adicionales no cubiertas.

4. **K optimo inconsistente:** El metodo del codo y el Silhouette Score a veces sugieren K diferentes. Se implemento logica de consenso.

5. **DBSCAN eps sensible:** El parametro eps de DBSCAN requiere ajuste por clinica ya que la densidad del espacio de features varia con el tamano de la poblacion.

---

## Acciones de Mejora

| Accion | Responsable | Sprint |
|--------|-------------|--------|
| Expandir diccionario de abreviaturas con feedback de medicos | Said | Backlog |
| Agregar mas anotaciones NER para diagnosticos complejos | Said | Backlog |
| Implementar ajuste automatico de eps en DBSCAN | Said | Sprint 4 (RAG) |

---

## Metricas del Sprint

| Metrica | Valor |
|---------|-------|
| Story points completados | 42 |
| Tests escritos | 68 |
| Coverage alcanzado | 81% |
| Modelos entrenados | 5 (NER, RF, SVM, GB, Autoencoder) |
| Datos sinteticos generados | 3,000 documentos |
| Entidades NER distintas | 15 tipos |
| Bugs encontrados | 5 |
| Bugs resueltos | 5 |

---

## Commits del Sprint

- `feat(nlp): implement SpaCy NER, NLTK cleaner, HuggingFace classifier, and BS4 scraper` (v0.3.0)
- `feat(ml): implement supervised classifiers, TF anomaly detector, and risk clustering` (v0.4.0)

---

## Demo

Al final del sprint, dado texto OCR de una receta, el sistema puede:
1. Limpiar el texto y corregir artefactos OCR (NLTK TextCleaner)
2. Extraer: medicamento, dosis, frecuencia, duracion, diagnostico (SpaCy NER)
3. Clasificar el documento como "receta" con >92% de confianza
4. Evaluar si los valores de laboratorio (si los hay) son anomalos
5. Asignar al paciente a un cluster de riesgo

---

*Sprint 2 completado: 11 Febrero 2026*
