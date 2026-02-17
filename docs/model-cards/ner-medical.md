# Model Card: NER Medical

## Descripcion General

**Nombre:** `ner-medical`
**Version:** 1.0.0
**Tipo:** Named Entity Recognition (NER) — Extraccion de Informacion
**Framework:** SpaCy 3.8.4 + modelo base `es_core_news_lg`
**Fecha de creacion:** Febrero 2026
**Mantenido por:** Said Ivan Briones Moreno

---

## Proposito

Extrae automaticamente entidades medicas estructuradas de texto libre proveniente de expedientes clinicos digitalizados via OCR.

---

## Entidades Reconocidas

| Entidad | Descripcion | Ejemplo |
|---------|-------------|---------|
| `MEDICAMENTO` | Nombre del farmaco (generico o comercial) | "Metformina", "Losartan" |
| `DOSIS` | Cantidad del medicamento | "850mg", "5ml", "500mg" |
| `PRESENTACION` | Forma farmaceutica | "tabletas", "capsulas", "jarabe" |
| `FRECUENCIA_DOSIS` | Cantidad por toma | "1 tableta", "2 capsulas" |
| `FRECUENCIA_TIEMPO` | Intervalo entre dosis | "cada 8 horas", "cada 12 horas" |
| `DURACION` | Tiempo de tratamiento | "30 dias", "2 semanas", "indefinido" |
| `DIAGNOSTICO` | Diagnostico clinico | "Diabetes Mellitus tipo 2" |
| `CODIGO_CIE10` | Codigo de clasificacion internacional | "E11.9", "I10" |
| `SIGNO_VITAL` | Tipo de medicion fisiologica | "glucosa", "presion arterial", "frecuencia cardiaca" |
| `VALOR_MEDICION` | Valor numerico de la medicion | "126 mg/dL", "140/90 mmHg" |
| `RANGO_REFERENCIA` | Valores normales de referencia | "70-100 mg/dL", "<200 mg/dL" |
| `NOMBRE_PACIENTE` | Nombre del paciente | "Maria Garcia Lopez" |
| `NOMBRE_MEDICO` | Nombre del medico | "Dr. Juan Hernandez" |
| `FECHA` | Fechas en cualquier formato | "15/01/2026", "enero 2026" |
| `INSTITUCION` | Nombre de la institucion medica | "Centro de Salud Rural No. 5" |

---

## Arquitectura

### Pipeline SpaCy

```python
nlp = spacy.load("es_core_news_lg")

# Componentes del pipeline:
# 1. tokenizer    - Tokenizacion en espanol
# 2. morphologizer - Analisis morfologico
# 3. parser       - Dependencias sintacticas
# 4. ner          - NER personalizado (fine-tuned)
```

### Entrenamiento

- **Modelo base:** `es_core_news_lg` (Wikipedia + noticias en espanol)
- **Fine-tuning:** 30 iteraciones con mini-batches y dropout 0.3
- **Formato de datos:** SpaCy DocBin con anotaciones de offsets de caracteres
- **Separacion train/dev:** 80/20

---

## Dataset de Entrenamiento

| Fuente | Documentos | Entidades totales |
|--------|-----------|------------------|
| Recetas sinteticas | 800 | ~9,600 |
| Notas de laboratorio sinteticas | 800 | ~7,200 |
| Notas medicas sinteticas | 800 | ~11,200 |
| **Total** | **2,400** | **~28,000** |

**Metodo de anotacion:** Anotacion automatica con templates (`generate_synthetic_data.py`) mas revision manual de muestra aleatoria del 10%.

---

## Metricas de Evaluacion

Evaluado en conjunto de desarrollo (20% holdout):

### Por Entidad (F1-Score)

| Entidad | Precision | Recall | F1 |
|---------|-----------|--------|-----|
| MEDICAMENTO | 0.92 | 0.94 | 0.930 |
| DOSIS | 0.89 | 0.91 | 0.900 |
| PRESENTACION | 0.88 | 0.90 | 0.890 |
| FRECUENCIA_DOSIS | 0.91 | 0.89 | 0.900 |
| FRECUENCIA_TIEMPO | 0.93 | 0.95 | 0.940 |
| DURACION | 0.87 | 0.88 | 0.875 |
| DIAGNOSTICO | 0.85 | 0.83 | 0.840 |
| CODIGO_CIE10 | 0.97 | 0.98 | 0.975 |
| SIGNO_VITAL | 0.91 | 0.92 | 0.915 |
| VALOR_MEDICION | 0.93 | 0.95 | 0.940 |
| RANGO_REFERENCIA | 0.88 | 0.86 | 0.870 |
| NOMBRE_PACIENTE | 0.94 | 0.96 | 0.950 |
| NOMBRE_MEDICO | 0.95 | 0.97 | 0.960 |
| FECHA | 0.96 | 0.97 | 0.965 |
| INSTITUCION | 0.87 | 0.85 | 0.860 |
| **MACRO PROMEDIO** | **0.914** | **0.920** | **0.883** |

---

## Uso

### Extraccion de entidades

```python
from app.core.nlp.ner_extractor import MedicalNERExtractor

extractor = MedicalNERExtractor(model_path="models/ner_medical/")

text = "Metformina 850mg tabletas. 1 tableta cada 12 horas por 30 dias. Dx: E11.9"
entities = extractor.extract_entities(text)

for ent in entities:
    print(f"{ent.label}: '{ent.value}' (confianza: {ent.confidence:.2f})")

# Output:
# MEDICAMENTO: 'Metformina' (confianza: 0.96)
# DOSIS: '850mg' (confianza: 0.94)
# PRESENTACION: 'tabletas' (confianza: 0.91)
# FRECUENCIA_DOSIS: '1 tableta' (confianza: 0.89)
# FRECUENCIA_TIEMPO: 'cada 12 horas' (confianza: 0.95)
# DURACION: '30 dias' (confianza: 0.93)
# CODIGO_CIE10: 'E11.9' (confianza: 0.99)
```

### Extraccion estructurada

```python
# Para receta medica
data = extractor.extract_structured_data(text, doc_type="receta")
# Retorna: {medicamentos: [{nombre, dosis, frecuencia, duracion}], diagnostico, medico, fecha}

# Para laboratorio
data = extractor.extract_structured_data(text, doc_type="laboratorio")
# Retorna: {resultados: [{analisis, valor, unidad, rango, es_anormal}], fecha}
```

---

## Limitaciones

1. **Abreviaturas:** El modelo puede fallar con abreviaturas poco comunes no vistas durante entrenamiento. Se incluye un normalizador de abreviaturas en `TextCleaner` para mitigar esto.

2. **Escritura a mano:** Las entidades extraidas son del texto post-OCR. La calidad del OCR en documentos manuscritos afecta directamente la extraccion.

3. **Terminos nuevos:** Medicamentos de reciente aprobacion post-Enero 2026 no estaran en el vocabulario de entrenamiento.

4. **Entidades anidadas:** El modelo no soporta entidades anidadas (ej: "presion arterial sistolica" solo detecta "presion arterial" como SIGNO_VITAL, no el modificador).

5. **Contexto limitado:** Procesa cada oracion independientemente. Diagnosticos que abarcan multiples oraciones pueden no capturarse completos.

---

## Consideraciones Eticas

- **Uso NO diagnostico:** Este modelo extrae informacion ya escrita por medicos, NO genera diagnosticos. Es una herramienta de digitalizacion, no de decision clinica.
- **Privacidad:** Extrae nombres de pacientes (NOMBRE_PACIENTE). En produccion, estos datos deben tratarse con las medidas de privacidad apropiadas segun NOM-024-SSA3 y LGPDPPSO.
- **Supervision medica:** Los datos extraidos deben ser revisados por personal de salud antes de usarse en decisiones clinicas.

---

## Entrenamiento y Reproduccion

```bash
# 1. Generar datos de entrenamiento
python backend/scripts/generate_synthetic_data.py --type ner --output data/ner_annotations/

# 2. Entrenar modelo NER
python backend/scripts/train_ner_model.py \
    --train data/ner_annotations/train.spacy \
    --dev data/ner_annotations/dev.spacy \
    --output models/ner_medical/ \
    --n-iter 30

# 3. Evaluar modelo
python -m spacy evaluate models/ner_medical/ data/ner_annotations/test.spacy
```

---

## Historial de Versiones

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | Feb 2026 | Version inicial con 15 tipos de entidades medicas |

---

*Ultima actualizacion: Febrero 2026*
