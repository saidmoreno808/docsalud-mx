# Model Card: Risk Clusterer

## Descripcion General

**Nombre:** `risk-clusterer`
**Version:** 1.0.0
**Tipo:** Clustering no supervisado + Scoring de riesgo
**Framework:** Scikit-learn 1.6.1
**Fecha de creacion:** Febrero 2026
**Mantenido por:** Said Ivan Briones Moreno

---

## Proposito

Agrupa pacientes en clusters segun su perfil de riesgo clinico utilizando aprendizaje no supervisado. Permite identificar poblaciones de pacientes con caracteristicas similares y estimar su nivel de riesgo relativo para priorizar la atencion medica.

**Valor clinico:**
- Identificar pacientes en riesgo alto antes de que desarrollen complicaciones
- Segmentar poblacion para intervenciones preventivas focalizadas
- Apoyar la gestion de recursos en clinicas con alta demanda
- Detectar outliers (casos atipicos que pueden ser los mas criticos)

---

## Algoritmos Implementados

### 1. K-Means

- **Proposito:** Clustering principal, asigna cada paciente a uno de K clusters
- **K optimo:** Calculado con metodo del codo + Silhouette Score (tipicamente 4-6 clusters)
- **Inicializacion:** k-means++ para convergencia estable
- **Iteraciones:** max_iter=300, n_init=10

### 2. DBSCAN

- **Proposito:** Clustering de forma arbitraria + deteccion de outliers
- **Outliers (label=-1):** Pacientes que no pertenecen a ningun cluster — casos atipicos de alta prioridad
- **Parametros:** eps=0.5, min_samples=5 (calibrados para el espacio de features medico)

### 3. PCA para visualizacion

- **Componentes:** 2 (para grafica 2D)
- **Varianza explicada objetivo:** >75%

---

## Features del Paciente

| Feature | Tipo | Descripcion |
|---------|------|-------------|
| `edad` | Numerica | Edad en anos |
| `es_hombre` | Binaria | 1=hombre, 0=mujer |
| `num_condiciones_cronicas` | Entera | Numero de condiciones cronicas diagnosticadas |
| `num_medicamentos` | Entera | Cantidad de medicamentos activos |
| `visitas_6_meses` | Entera | Numero de visitas en los ultimos 6 meses |
| `dias_desde_ultima_consulta` | Numerica | Dias sin consulta (inverso de adherencia) |
| `glucosa_normalizada` | Float 0-1 | Ultimo valor de glucosa normalizado |
| `hemoglobina_normalizada` | Float 0-1 | Ultimo valor de hemoglobina normalizado |
| `presion_sistolica_norm` | Float 0-1 | Ultima presion sistolica normalizada |
| `num_alertas_previas` | Entera | Numero de alertas generadas previamente |
| `score_anomalia_lab` | Float 0-1 | Score del autoencoder de anomalias |

**Preprocesamiento:** StandardScaler (media=0, std=1) aplicado antes del clustering.

---

## Descripcion de los Clusters

Los clusters tipicos encontrados en datos de clinicas rurales:

| Cluster | Nombre | Caracteristicas | Riesgo |
|---------|--------|-----------------|--------|
| 0 | **Bajo Riesgo** | Jovenes, pocas condiciones, labs normales, visitas regulares | Bajo |
| 1 | **Riesgo Metabolico** | Glucosa elevada, multiples medicamentos, condiciones cronicas | Medio-Alto |
| 2 | **Adultos Mayor Controlados** | >60 anos, condiciones cronicas pero bien controladas, adherentes | Medio |
| 3 | **Perdida de Seguimiento** | Muchos dias sin consulta, labs desactualizados | Medio-Alto |
| 4 | **Alto Riesgo Activo** | Multiples anomalias en labs, muchas alertas previas, condiciones descontroladas | Alto |
| -1 | **Outliers DBSCAN** | Perfil atipico, requieren evaluacion individual inmediata | Critico |

*Nota: La descripcion exacta de clusters varia segun los datos reales de cada clinica.*

---

## Metricas de Evaluacion

| Metrica | K-Means | DBSCAN |
|---------|---------|--------|
| Silhouette Score | 0.672 | 0.641 |
| Davies-Bouldin Index | 0.854 | N/A |
| Calinski-Harabasz | 1,247 | N/A |
| % Outliers (DBSCAN) | N/A | 3.2% |
| K optimo (metodo del codo) | 5 | N/A |

**Interpretacion del Silhouette 0.672:** Los clusters son bien definidos (>0.5 se considera buena separacion). Valores cercanos a 1.0 indicarian clusters perfectamente separados.

---

## Uso

### Clustering basico

```python
from app.core.ml.risk_clusterer import RiskClusterer
import numpy as np

clusterer = RiskClusterer()

# Features de pacientes (n_patients, n_features)
patient_features = np.array([...])  # (n, 11)

# K-Means
kmeans_result = clusterer.fit_kmeans(patient_features)
print(kmeans_result["labels"])       # Array de cluster por paciente
print(kmeans_result["silhouette"])   # Score de calidad
print(kmeans_result["descriptions"]) # Descripcion interpretable

# DBSCAN
dbscan_result = clusterer.fit_dbscan(patient_features)
outliers = np.where(dbscan_result["labels"] == -1)[0]
print(f"Pacientes atipicos: {len(outliers)}")

# Visualizacion PCA
img_path = clusterer.visualize_clusters(patient_features, kmeans_result["labels"])
```

### Re-clustering periodico

```bash
# Recomendado: re-correr mensualmente con datos actualizados
python backend/scripts/update_risk_clusters.py \
    --date $(date +%Y-%m) \
    --output models/risk_clusterer/
```

---

## Score de Riesgo Individual

Ademas del cluster, cada paciente recibe un `risk_score` continuo (0.0 - 1.0):

```python
# Calculado por RiskScorer basado en:
# - Cluster asignado (base score)
# - Anomaly score del autoencoder
# - Numero de alertas activas
# - Dias sin consulta
# - Condiciones cronicas no controladas

risk_score = risk_scorer.calculate(patient_data)
# 0.0-0.3: Bajo riesgo (verde)
# 0.3-0.6: Riesgo moderado (amarillo)
# 0.6-0.8: Alto riesgo (naranja)
# 0.8-1.0: Riesgo critico (rojo)
```

---

## Limitaciones

1. **No causal:** El clustering identifica grupos similares, no causa-efecto. Un paciente en cluster "alto riesgo" no necesariamente desarrollara complicaciones.

2. **Datos longitudinales:** El modelo opera en snapshot actual. Historiales mas ricos (tendencias temporales) podrian mejorar la precision del clustering.

3. **Sesgo de seleccion:** Pacientes que no asisten regularmente tendran features desactualizadas, lo que puede distorsionar su clasificacion de riesgo.

4. **Estabilidad:** Los clusters cambian cada vez que se re-entrena. Se recomienda etiquetar clusters semanticamente en lugar de por numero para mantener consistencia.

5. **Tamano minimo:** Se necesitan al menos 50 pacientes para que el clustering sea estadisticamente significativo. Con menos pacientes, usar solo las reglas del `rules_engine.py`.

6. **Outliers DBSCAN:** Son los casos mas importantes clinicamente pero el algoritmo no los "explica" — requieren revision medica directa.

---

## Consideraciones Eticas

- **Equidad:** Verificar que el clustering no cree grupos sesgados por datos demograficos irrelevantes (ej: nivel socioeconomico implicito en frecuencia de visitas).
- **Transparencia:** Los factores que determinan el cluster de cada paciente se muestran al medico. No es una caja negra.
- **No discriminacion:** El risk_score se usa para priorizar atencion preventiva, NUNCA para negar atencion medica.
- **Revision periodica:** Los clusters deben ser revisados por personal medico para validar que la segmentacion tiene sentido clinico.

---

## Entrenamiento y Reproduccion

```bash
# Extraer features de pacientes de la DB
python backend/scripts/extract_patient_features.py --output data/patient_features.csv

# Entrenar clusterer
python backend/scripts/train_risk_clusterer.py \
    --data data/patient_features.csv \
    --output models/risk_clusterer/ \
    --max-k 10

# Visualizar resultados
python backend/scripts/visualize_clusters.py \
    --model models/risk_clusterer/ \
    --data data/patient_features.csv

# Actualizar clusters en DB
python backend/scripts/update_patient_clusters.py --model models/risk_clusterer/
```

---

## Visualizacion

El modelo genera automaticamente:
1. **Grafica del codo:** Para determinar K optimo
2. **Grafica de silhouette:** Para evaluar separacion de clusters
3. **PCA 2D:** Visualizacion de clusters en 2 dimensiones
4. **Heatmap de features:** Valores promedio de cada feature por cluster

Imagenes guardadas en: `models/risk_clusterer/plots/`

---

## Historial de Versiones

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | Feb 2026 | Version inicial con K-Means + DBSCAN + score continuo |

---

*Ultima actualizacion: Febrero 2026*
