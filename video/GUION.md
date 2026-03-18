# ClinicaIA — Guion de Video Demo
**Hackathon:** DigitalOcean Gradient AI Hackathon 2026
**Duración total:** ~3 minutos (180s · 30fps · 5260 frames)
**Resolución:** 1920 × 1080 · H.264
**Archivo de composición:** `video/src/ClinicaIAVideo.tsx`

---

## Estructura de escenas

| # | Escena | Duración | Frames | Archivo |
|---|--------|----------|--------|---------|
| 1 | Título + Hook | 15s | 450 | `TitleScene.tsx` |
| — | *Transición: fade* | 0.67s | 20 | — |
| 2 | El Problema | 25s | 750 | `ProblemScene.tsx` |
| — | *Transición: slide from-right* | 0.67s | 20 | — |
| 3 | La Solución — Pipeline | 20s | 600 | `SolutionFlowScene.tsx` |
| — | *Transición: fade* | 0.67s | 20 | — |
| 4 | Demo — Upload | 25s | 750 | `DemoUploadScene.tsx` |
| — | *Transición: slide from-bottom* | 0.67s | 20 | — |
| 5 | Demo — Análisis Pipeline | 30s | 900 | `DemoAnalysisScene.tsx` |
| — | *Transición: fade* | 0.67s | 20 | — |
| 6 | Demo — Resultado IA | 35s | 1050 | `DemoResultScene.tsx` |
| — | *Transición: slide from-right* | 0.67s | 20 | — |
| 7 | Stack Tecnológico | 15s | 450 | `TechStackScene.tsx` |
| — | *Transición: fade* | 0.67s | 20 | — |
| 8 | CTA Final | 15s | 450 | `CTAScene.tsx` |

**Total neto:** 180s − 7×0.67s = **~175.3s** (~5260 frames)

---

## Guion detallado por escena

---

### ESCENA 1 — Título (0:00 – 0:15)
**Archivo:** `video/src/scenes/TitleScene.tsx`
**Fondo:** `#0a0e1a` con círculos radiales teal/índigo difusos

#### Animaciones
- **0:00–0:05** — Cruz médica SVG + logotipo "ClinicaIA" entran con `spring(damping:12)` desde escala 0, fade-in
- **0:06–0:10** — Tagline *"Inteligencia Artificial para el Expediente Clínico"* sube 60px con `spring(damping:200)` + fade
- **0:09–0:12** — Subtítulo *"OCR · NLP · RAG · LLM — del papel al diagnóstico en segundos"* fade-in
- **0:11–0:15** — Badge DigitalOcean *"Gradient AI Hackathon 2026"* aparece desde abajo + fade
- **Continuo** — Pulso de brillo sutil en el gradiente del logo (seno suavizado)

#### Narración sugerida
> *"ClinicaIA — inteligencia artificial aplicada al expediente clínico. Del papel al diagnóstico en segundos."*

---

### ESCENA 2 — El Problema (0:15 – 0:40)
**Archivo:** `video/src/scenes/ProblemScene.tsx`
**Fondo:** Radial rojo difuso superior derecho

#### Animaciones
- **0:15** — Badge "EL PROBLEMA" + H1 slide-down fade
- **0:15.5** — Tarjeta stat **"1B+"** registros médicos en papel → spring entrance Y+50
- **0:16** — Tarjeta stat **"4.2h"** promedio digitalización manual → spring con delay
- **0:16.5** — Tarjeta stat **"34%"** errores en transcripción → spring con delay
- **0:18** — Bullet 1: *"Médicos pierden horas en tareas administrativas..."* slide desde izquierda
- **0:19** — Bullet 2: *"Información crítica dispersa sin estructura..."* slide
- **0:20** — Bullet 3: *"Diagnósticos tardíos por imposibilidad de acceder al historial..."* slide

#### Narración sugerida
> *"En México, más de mil millones de registros médicos siguen en papel. Cuatro horas promedio para digitalizar un expediente. Un 34% de errores en transcripción manual. Los médicos pierden tiempo valioso en administración cuando deberían estar atendiendo pacientes."*

---

### ESCENA 3 — La Solución · Pipeline (0:40 – 1:00)
**Archivo:** `video/src/scenes/SolutionFlowScene.tsx`
**Fondo:** Dark + glow teal central

#### Animaciones
- **0:40** — Badge "LA SOLUCIÓN" + H1 fade-down
- **0:40.3** — Nodo 1 **Documento** aparece con `spring(damping:14)` scale 0.5→1
- **0:40.7** — Nodo 2 **OCR** + flecha animada (ancho 0→100%) entre nodos
- **0:41** — Nodo 3 **NLP** + flecha
- **0:41.3** — Nodo 4 **RAG** + flecha
- **0:41.6** — Nodo 5 **DO AI** + flecha (con borde punteado "Gradient AI")
- **0:41.9** — Nodo 6 **Diagnóstico** + flecha
- **0:42.5** — Badge teal "do · Gradient AI" debajo del nodo DO AI

#### Nodos del pipeline
```
📄 Documento → 🔍 OCR → 🧠 NLP → 📦 RAG → 🤖 DO AI → 💊 Diagnóstico
(PDF/imagen)  (Tesseract) (SpaCy) (pgvector) (Llama 3.3) (Análisis IA)
```

#### Narración sugerida
> *"ClinicaIA conecta seis capas tecnológicas: extracción OCR, análisis NLP, indexación vectorial, recuperación semántica, e inferencia con Llama 3.3 70B a través del nuevo DO Gradient AI de DigitalOcean."*

---

### ESCENA 4 — Demo: Upload (1:00 – 1:25)
**Archivo:** `video/src/scenes/DemoUploadScene.tsx`
**URL demo real:** `https://clinicaia-docsalud-tk3ds.ondigitalocean.app`

#### Animaciones
- **1:00** — Badge "DEMO — PASO 1" + H1 fade
- **1:01** — Browser mockup (con barra URL real de DO) entra con `spring(damping:200)` Y+80
- **1:00–1:25** — Drop zone pulsa suavemente con `sin()` oscillation
- **1:02** — Bullet cards derechas aparecen con slide + fade staggered
- **1:02** — Zona de drop cambia a estado *drag-over* (borde teal, fondo sutil, texto cambia)
- **1:03** — Archivo **"expediente_juan_garcia_2024.pdf · 2.4MB"** cae con spring bounce
- **1:04** — Botón **"🔬 Analizar Expediente"** aparece con spring scale 0.8→1
- **1:05.5** — Flash de click en el botón (flash + fade)
- **Continuo** — Flecha pulsante → *"Un clic para iniciar el análisis"*

#### Notas de producción
> Si se graba pantalla real, reemplazar el browser mockup con `<Video src={staticFile("demo-upload.mp4")} />` en este componente.

#### Narración sugerida
> *"Desde la interfaz web — sin instalación — el médico arrastra el expediente escaneado. Un clic es suficiente para iniciar el análisis completo."*

---

### ESCENA 5 — Demo: Análisis (1:25 – 1:55)
**Archivo:** `video/src/scenes/DemoAnalysisScene.tsx`

#### Animaciones — Pipeline de pasos
- **1:25** — Badge "DEMO — PASO 2" + H1
- **1:25.3** — Step 1 **Extracción OCR** aparece → spinner (rotación interpolada) → barra de progreso 0→100% en 3s → badge "COMPLETADO" + checkmark ✓
- **1:28** — Step 2 **Análisis NLP/NER** activo → progreso 2.5s
- **1:30.5** — Step 3 **Indexación vectorial** activo → progreso 2s
- **1:32.5** — Step 4 **Inferencia DO Gradient AI** activo → progreso 2s

#### Animaciones — Panel NER (aparece en segundo 5.5 de escena)
Tokens etiquetados aparecen con stagger (fade + Y) uno a uno:
- 🟢 `Juan García López` **[PACIENTE]**
- 🔴 `hipertensión arterial` **[DX]**
- 🔵 `Losartán 50mg` **[MED]**
- 🟡 `12/03/2025` **[FECHA]**
- 🟣 `Dra. María Torres` **[MEDICO]**

Métricas finales: **847 tokens · 23 entidades · 97% confianza**

#### Narración sugerida
> *"El sistema procesa el documento en etapas: OCR extrae el texto, SpaCy identifica entidades médicas — diagnósticos, medicamentos, fechas, médico tratante. Todo vectorizado en pgvector y enviado a Llama 3.3 en DO Gradient AI."*

---

### ESCENA 6 — Demo: Resultado (1:55 – 2:30)
**Archivo:** `video/src/scenes/DemoResultScene.tsx`

#### Animaciones
- **1:55** — Badge "DEMO — RESULTADO" + H1
- **1:55.5** — Panel `DiagnosticPanel` entra con `spring(damping:200)` Y+60
- **1:56** — 3 tarjetas diagnóstico en fila (spring stagger):
  - 🩺 **Hipertensión Arterial** Grado II — CIE-10: I10
  - 💊 **Losartán 50mg** — 1 vez al día
  - ⚠️ **Riesgo MODERADO** — Score 0.62
- **1:57.5** — Texto IA: efecto typewriter ~280 chars en 1.5s con cursor parpadeante `sin(frame*0.3)`
- **2:02.5** — Título "Confianza por categoría" fade
- **2:02.6** — Barra **Diagnóstico principal 94%** — spring width 0→94%
- **2:02.9** — Barra **Medicación 97%** — spring width
- **2:03.2** — Barra **Plan de seguimiento 88%** — spring width
- **2:03.5** — Panel recomendaciones (5 items, stagger slide+fade)
- **2:05** — Badge ⚡ **"Tiempo total: 3.2 segundos"**

#### Texto IA (typewriter)
> *"Paciente masculino de 58 años con diagnóstico confirmado de hipertensión arterial grado II. Medicación actual: Losartán 50mg/día. Antecedentes familiares positivos para enfermedad cardiovascular. Se recomienda monitoreo cada 3 meses y valorar ajuste de dosis según respuesta al tratamiento. No se identificaron interacciones medicamentosas relevantes."*

#### Recomendaciones IA
1. 📅 Control de presión arterial cada 3 meses
2. 🥗 Dieta baja en sodio (<2g/día) y actividad física moderada
3. 🔬 Evaluar función renal semestral (creatinina, potasio)
4. 💊 Considerar ajuste de Losartán si PA >140/90 mmHg
5. 🏥 Consulta con cardiología si riesgo aumenta a alto

#### Narración sugerida
> *"El resultado: un panel diagnóstico estructurado en menos de cuatro segundos. Diagnóstico codificado en CIE-10, medicación actual, nivel de riesgo, análisis narrativo de Llama 3.3 y recomendaciones clínicas accionables."*

---

### ESCENA 7 — Stack Tecnológico (2:30 – 2:45)
**Archivo:** `video/src/scenes/TechStackScene.tsx`

#### Animaciones
- **2:30** — Badge "STACK TECNOLÓGICO" + H1 fade
- **2:30.3 – 2:31.4** — 8 tarjetas tech grid con spring stagger (scale 0.7→1, delay 150ms):

| Icono | Tecnología | Rol |
|-------|-----------|-----|
| ⚡ | **FastAPI** | Backend async Python |
| ⚛️ | **React 18** | Frontend TypeScript |
| 🐘 | **PostgreSQL** | pgvector 384d |
| 🔍 | **Tesseract** | OCR español |
| 🧠 | **SpaCy** | NLP/NER es |
| 🤖 | **Llama 3.3** | DO Gradient AI |
| 🐋 | **Docker** | Compose + NGINX |
| 🌊 | **DigitalOcean** | App Platform |

- **2:31.6** — Texto *"Desplegado en DO App Platform con Gradient AI inference y Managed PostgreSQL"*

#### Narración sugerida
> *"Stack completo de producción: FastAPI, React, PostgreSQL con pgvector, Tesseract OCR, SpaCy NLP — todo desplegado en DigitalOcean App Platform con inferencia vía Gradient AI."*

---

### ESCENA 8 — CTA Final (2:45 – 3:00)
**Archivo:** `video/src/scenes/CTAScene.tsx`
**Fondo:** Dark + radiales teal/índigo

#### Animaciones
- **2:45** — "ClinicaIA" H1 gradiente entra con `spring(damping:14)` scale 0.8→1 + glow pulsante
- **2:45.5** — Subtítulo fade: *"Del expediente en papel al diagnóstico asistido por IA en menos de 5 segundos"*
- **2:46** — Badge link 🌐 **Demo** → `clinicaia-docsalud-tk3ds.ondigitalocean.app` spring Y+30
- **2:46.3** — Badge link 💻 **GitHub** → `github.com/saidmoreno808/docsalud-mx`
- **2:46.6** — Badge link 🏆 **Hackathon** → `DigitalOcean Gradient AI Hackathon — Marzo 2026`
- **2:47** — Badge DO *"Powered by DigitalOcean · Gradient AI · App Platform · Managed PG"*

#### Narración sugerida
> *"ClinicaIA — disponible ahora en DigitalOcean. Prueba el demo en vivo, explora el código en GitHub, y únete al futuro de la medicina digital."*

---

## Comandos de preview y render

```bash
# Instalar dependencias
cd video && npm install

# Abrir Remotion Studio (preview interactivo)
npx remotion studio
# → http://localhost:3000

# Render completo a MP4
npx remotion render src/index.ts ClinicaIAVideo out/clinicaia-demo.mp4 \
  --codec=h264 \
  --jpeg-quality=80 \
  --concurrency=4

# Render de una escena para prueba (frames 0-449 = TitleScene)
npx remotion render src/index.ts ClinicaIAVideo out/title-test.mp4 \
  --frames=0-449

# Render de escena de resultado (frames ~3285-4334)
npx remotion render src/index.ts ClinicaIAVideo out/result-test.mp4 \
  --frames=3285-4334
```

---

## Integración con demo real (opcional)

Para reemplazar las animaciones simuladas con grabaciones reales del demo:

1. Grabar pantalla de `https://clinicaia-docsalud-tk3ds.ondigitalocean.app`
2. Guardar clips en `video/public/`:
   - `demo-upload.mp4` — flujo de carga de archivo
   - `demo-analysis.mp4` — pantalla de análisis en progreso
   - `demo-result.mp4` — panel DiagnosticPanel completo
3. En cada escena de demo, reemplazar el mockup con:
   ```tsx
   import { Video, staticFile } from "remotion";
   <Video src={staticFile("demo-upload.mp4")} />
   ```

---

## Paleta de colores

| Variable | Hex | Uso |
|----------|-----|-----|
| `BRAND` | `#00C4A1` | Color principal teal — ClinicaIA |
| `ACCENT` | `#6366F1` | Índigo — NLP, transiciones |
| `BG` | `#0a0e1a` | Fondo negro profundo |
| `DANGER` | `#EF4444` | Rojo — problema, diagnóstico |
| `SUCCESS` | `#10B981` | Verde — completado, resultados |
| `WARNING` | `#F59E0B` | Ámbar — riesgo moderado, stats |
| `DO_BLUE` | `#0080FF` | Azul DigitalOcean |

---

*Generado automáticamente · ClinicaIA © 2026*
