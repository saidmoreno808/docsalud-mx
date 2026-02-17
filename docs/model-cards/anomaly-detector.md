# Model Card: Anomaly Detector

## Descripcion General

**Nombre:** `anomaly-detector`
**Version:** 1.0.0
**Tipo:** Deteccion de anomalias no supervisada (Autoencoder)
**Framework:** TensorFlow 2.18 / Keras 3.8
**Fecha de creacion:** Febrero 2026
**Mantenido por:** Said Ivan Briones Moreno

---

## Proposito

Detecta valores anomalos en resultados de laboratorio de pacientes. Identifica mediciones que se desvian significativamente de los patrones normales, potencialmente indicando condiciones criticas que requieren atencion medica.

**Casos de uso:**
- Identificar resultados de glucosa extremadamente altos/bajos
- Detectar valores de hemoglobina fuera de rango critico
- Alertar sobre perfil hepatico o renal alterado
- Identificar combinaciones anomalas de valores (ej: sodio alto + potasio bajo)

---

## Arquitectura

### Autoencoder Denso

```
Input (input_dim)
    │
    ▼
[ENCODER]
Dense(64, ReLU) → BatchNormalization → Dropout(0.3)
Dense(32, ReLU) → BatchNormalization → Dropout(0.2)
Dense(16, ReLU)          ← LATENT SPACE (bottleneck)
    │
    ▼
[DECODER]
Dense(32, ReLU) → BatchNormalization
Dense(64, ReLU) → BatchNormalization
Dense(input_dim, Sigmoid)
    │
    ▼
Output (reconstruccion)
```

**Loss:** Mean Squared Error (MSE)
**Optimizer:** Adam(lr=1e-3)
**Callbacks:** EarlyStopping(patience=10) + ReduceLROnPlateau(patience=5)

### Logica de deteccion

```
reconstruction_error = MSE(input, reconstructed)
threshold = percentile_95(errors_on_training_set)

if reconstruction_error > threshold:
    es_anomalia = True
    anomaly_score = reconstruction_error / threshold
```

---

## Features de Entrada

El modelo procesa vectores numericos normalizados de resultados de laboratorio:

| Feature | Unidad | Rango Normal | Rango Critico |
|---------|--------|-------------|--------------|
| Glucosa en ayuno | mg/dL | 70-100 | <40 o >500 |
| Hemoglobina | g/dL | H: 13.5-17.5, M: 12-15.5 | <7 o >20 |
| Hematocrito | % | H: 41-53, M: 36-46 | <20% |
| Leucocitos | x10^3/uL | 4.5-11 | <2 o >30 |
| Plaquetas | x10^3/uL | 150-400 | <50 o >1000 |
| Creatinina | mg/dL | H: 0.7-1.3, M: 0.5-1.1 | >10 |
| BUN | mg/dL | 7-20 | >100 |
| ALT (TGP) | U/L | <56 | >500 |
| AST (TGO) | U/L | <40 | >500 |
| Colesterol total | mg/dL | <200 | >400 |
| Trigliceridos | mg/dL | <150 | >1000 |
| Sodio | mEq/L | 136-145 | <120 o >160 |
| Potasio | mEq/L | 3.5-5.0 | <2.5 o >6.5 |

---

## Dataset de Entrenamiento

**IMPORTANTE: El autoencoder se entrena SOLO con datos normales.**

| Conjunto | Pacientes simulados | Analisis por paciente |
|----------|--------------------|-----------------------|
| Datos normales (entrenamiento) | 5,000 | 13 analitos |
| Datos anómalos (solo evaluacion) | 500 | 13 analitos |

**Generacion:** Valores normales generados con distribuciones gaussianas calibradas con rangos de referencia clinicos del IMSS. Los datos anomalos se generaron introduciendo desviaciones controladas para evaluacion.

---

## Metricas de Evaluacion

| Metrica | Valor |
|---------|-------|
| AUC-ROC | 0.942 |
| Precision (anomalia) | 0.87 |
| Recall (anomalia) | 0.91 |
| F1 (anomalia) | 0.89 |
| False Positive Rate | 0.043 |
| Threshold (percentil 95) | 0.0847 |

**Interpretacion del AUC-ROC 0.942:** El modelo puede distinguir entre datos normales y anomalos con un 94.2% de efectividad.

**Trade-off elegido:** Se prioriza recall alto (evitar falsos negativos en clinica medica) sobre precision maxima.

---

## Uso

### Deteccion basica

```python
from app.core.ml.anomaly_detector import LabAnomalyDetector
import numpy as np

detector = LabAnomalyDetector()
detector.load("models/anomaly_detector/")

# Vector de valores de laboratorio normalizados
# [glucosa, hemoglobina, hematocrito, leucocitos, ...]
lab_vector = np.array([[0.8, 0.6, 0.7, 0.5, 0.6, 0.4, 0.3, 0.7, 0.6, 0.5, 0.4, 0.7, 0.6]])

results = detector.detect_anomalies(lab_vector)

for result in results:
    print(f"Anomalia: {result.is_anomaly}")
    print(f"Score: {result.anomaly_score:.3f}")
    print(f"Features anomalas: {result.top_anomalous_features}")
```

### Integracion en pipeline

```python
# Automatico al procesar resultados de laboratorio
# El AlertService llama al detector despues de extraer valores con NLP
```

---

## Umbrales de Severidad

| Anomaly Score | Severidad | Accion recomendada |
|--------------|-----------|-------------------|
| < 1.0 | Normal | Ningun alerta |
| 1.0 - 1.5 | Bajo | Registro en sistema |
| 1.5 - 2.5 | Medio | Alerta al medico |
| 2.5 - 4.0 | Alto | Notificacion urgente |
| > 4.0 | Critico | Alerta inmediata |

---

## Limitaciones

1. **Entrenado en poblacion general:** Los rangos normales pueden variar segun edad, sexo, embarazo, altitud (importante en Mexico), y condiciones preexistentes. El modelo puede generar falsos positivos en pacientes con condiciones cronicas controladas.

2. **Requiere todos los features:** El modelo necesita los 13 analitos. Si faltan valores, se imputa con la media, lo que puede reducir la sensibilidad para esos analitos.

3. **No causal:** El modelo detecta anomalias estadisticas, no diagnostica causas. Un resultado anonimo requiere interpretacion medica.

4. **Deriva temporal:** Los patrones de laboratorio pueden cambiar con nuevos equipos o reactivos en las clinicas. Se recomienda re-entrenar periodicamente con datos recientes.

5. **Sensibilidad al ruido:** Errores de OCR en los valores numericos pueden generar falsos positivos. Se recomienda validar la extraccion NLP antes de ejecutar el detector.

---

## Consideraciones Eticas

- **Herramienta de apoyo:** El detector es un sistema de alerta temprana, no un diagnostico. Un medico calificado debe interpretar cada alerta.
- **Equidad:** Validar que el modelo funcione equitativamente en distintos grupos demograficos (edad, sexo, region).
- **Transparencia:** El score de anomalia y las features responsables se muestran al medico para facilitar la interpretacion.
- **Auditoria:** Todos los casos detectados como anomalos se registran en la base de datos para revision y mejora continua.

---

## Entrenamiento y Reproduccion

```bash
# Generar datos de laboratorio sinteticos
python backend/scripts/generate_synthetic_data.py --type lab --output data/lab_data/ --n 5500

# Entrenar autoencoder
python backend/scripts/train_anomaly_detector.py \
    --data data/lab_data/normal_train.csv \
    --output models/anomaly_detector/ \
    --epochs 100 \
    --batch-size 32

# Evaluar con datos anomalos
python backend/scripts/evaluate_models.py \
    --model anomaly \
    --normal data/lab_data/normal_test.csv \
    --anomalous data/lab_data/anomalous.csv
```

---

## Historial de Versiones

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | Feb 2026 | Version inicial con 13 analitos |

---

*Ultima actualizacion: Febrero 2026*
