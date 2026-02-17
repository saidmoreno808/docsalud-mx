# Model Card: Document Classifier

## Descripcion General

**Nombre:** `document-classifier`
**Version:** 1.0.0
**Tipo:** Clasificador multiclase (supervisado)
**Framework principal:** Scikit-learn 1.6.1 + HuggingFace Transformers 4.47.1
**Fecha de creacion:** Febrero 2026
**Mantenido por:** Said Ivan Briones Moreno

---

## Proposito

Clasifica automaticamente documentos medicos digitalizados en las siguientes categorias:

| Label | Descripcion | Ejemplos |
|-------|-------------|---------|
| `receta` | Prescripcion medica | Receta con medicamentos, dosis y diagnostico |
| `laboratorio` | Resultados de laboratorio | Biometria hematica, quimica sanguinea, EGO |
| `nota_medica` | Nota clinica o de evolucion | Nota de primera vez, seguimiento, urgencias |
| `referencia` | Referencia o contrarreferencia | Derivacion a especialidad, alta hospitalaria |
| `consentimiento` | Consentimiento informado | Autorizacion para procedimientos |
| `otro` | Documento no categorizado | Cualquier otro documento medico |

---

## Arquitectura

### Modelo Primario: Ensemble Sklearn

```python
Pipeline([
    TfidfVectorizer(max_features=5000, ngram_range=(1, 2)),
    VotingClassifier(
        estimators=[
            ("rf", RandomForestClassifier(n_estimators=200, max_depth=20)),
            ("svm", SVC(kernel="rbf", probability=True)),
            ("gb", GradientBoostingClassifier(n_estimators=200, learning_rate=0.1))
        ],
        voting="soft"
    )
])
```

### Modelo Secundario: HuggingFace Transformer

- **Base model:** `PlanTL-GOB-ES/roberta-base-biomedical-clinical-es`
- **Task head:** Sequence Classification (6 classes)
- **Fine-tuning:** 5 epochs, lr=2e-5, batch_size=16
- **Dropout:** 0.3 en capa de clasificacion

---

## Dataset de Entrenamiento

| Conjunto | Documentos | Metodo de generacion |
|----------|-----------|---------------------|
| Sintetico (principal) | 2,400 | `scripts/generate_synthetic_data.py` |
| Aumentado con variaciones OCR | 600 | Perturbaciones aleatorias |
| **Total** | **3,000** | |

**Distribucion por clase:**
- receta: 650 (22%)
- laboratorio: 650 (22%)
- nota_medica: 650 (22%)
- referencia: 500 (17%)
- consentimiento: 300 (10%)
- otro: 250 (8%)

**Fuente de datos:** Todos los datos son **100% sinteticos**. Generados con templates de documentos medicos mexicanos reales, con nombres y datos demograficos ficticios. Ninguna informacion de paciente real fue usada.

---

## Metricas de Evaluacion

Evaluado en conjunto de test (20% holdout):

| Metrica | Sklearn Ensemble | Transformer |
|---------|-----------------|-------------|
| Accuracy | 0.921 | 0.948 |
| F1-Macro | 0.915 | 0.943 |
| Precision-Macro | 0.918 | 0.946 |
| Recall-Macro | 0.912 | 0.940 |

**Por clase (Sklearn Ensemble):**

| Clase | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| receta | 0.94 | 0.96 | 0.95 |
| laboratorio | 0.95 | 0.94 | 0.945 |
| nota_medica | 0.89 | 0.91 | 0.90 |
| referencia | 0.91 | 0.88 | 0.895 |
| consentimiento | 0.93 | 0.90 | 0.915 |
| otro | 0.87 | 0.85 | 0.86 |

---

## Uso

### Inferencia basica

```python
from app.core.ml.document_classifier import SklearnDocumentClassifier

classifier = SklearnDocumentClassifier()
classifier.load("models/document_classifier/")

result = classifier.predict("Rx: Metformina 850mg tabletas\n1 tableta cada 12 horas por 30 dias")
print(result.label)       # "receta"
print(result.confidence)  # 0.94
print(result.probabilities)  # {"receta": 0.94, "laboratorio": 0.02, ...}
```

### Via API

```bash
curl -X POST https://docsaludmx.ochoceroocho.mx/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Glucosa en ayuno: 126 mg/dL (70-100)"}'
```

---

## Limitaciones

1. **Idioma:** Entrenado exclusivamente en espanol mexicano. Documentos en otras lenguas o dialectos regionales pueden clasificarse incorrectamente.

2. **Calidad del OCR:** La precision cae ~8-12% en documentos con OCR de baja calidad (<60% confianza). Se recomienda preprocesar con OpenCV antes de clasificar.

3. **Documentos mixtos:** Un documento que contiene receta Y resultados de laboratorio se clasificara segun el contenido dominante.

4. **Documentos muy cortos:** Fragmentos de menos de 20 palabras tienen precision reducida (~75%). El modelo necesita contexto suficiente.

5. **Documentos de especialidades:** Especialidades de nicho (oncologia, neurologia) con terminologia muy tecnica pueden clasificarse como `otro` con mayor frecuencia.

---

## Consideraciones Eticas

- **Sesgo:** El modelo fue entrenado con datos sinteticos basados en documentos de clinicas rurales mexicanas. Puede tener menor precision en documentos de hospitales de tercer nivel o especialidades.
- **Uso responsable:** Este clasificador es una herramienta de apoyo, NO un sistema de decision clinica autonoma. Siempre debe haber supervision medica.
- **Privacidad:** El modelo en si no almacena datos de pacientes. Los textos procesados no se registran a menos que el sistema de logging este activado.

---

## Entrenamiento y Reproduccion

```bash
# Generar datos sinteticos
python backend/scripts/generate_synthetic_data.py --output data/training/ --n 3000

# Entrenar clasificador Sklearn
python backend/scripts/train_classifier.py --data data/training/ --output models/document_classifier/

# Evaluar
python backend/scripts/evaluate_models.py --model models/document_classifier/ --test data/training/test/
```

---

## Historial de Versiones

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | Feb 2026 | Version inicial con ensemble Sklearn + Transformer |

---

*Ultima actualizacion: Febrero 2026*
