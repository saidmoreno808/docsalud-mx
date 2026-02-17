# Sprint 1 Retrospective — Fundamentos y OCR

**Sprint:** 1
**Periodo:** Febrero 2026, Semana 1
**Duracion:** 1 semana
**Equipo:** Said Ivan Briones Moreno (Solo Developer + AI Pair: Claude Code)
**Metodologia:** Scrum adaptado para equipo unipersonal

---

## Objetivo del Sprint

Establecer los fundamentos del proyecto (Fase 0) e implementar el modulo OCR completo (Fase 1) con pruebas unitarias.

---

## User Stories Completadas

| ID | Historia | Puntos | Estado |
|----|----------|--------|--------|
| DSM-001 | Como desarrollador, quiero la estructura base del proyecto con Docker y DB schema para comenzar a construir | 8 | Completado |
| DSM-002 | Como medico, quiero subir una foto de receta y obtener el texto extraido con alta precision | 13 | Completado |
| DSM-003 | Como desarrollador, quiero tests unitarios para el modulo OCR con >80% coverage | 5 | Completado |

**Total puntos completados:** 26/26 (100%)

---

## Lo Que Salio Bien

1. **Estructura del proyecto bien definida:** El `CLAUDE.md` como fuente unica de verdad resulto muy efectivo para mantener consistencia arquitectonica.

2. **Pipeline OCR robusto:** La combinacion OpenCV + Tesseract maneja bien los documentos medicos tipicos (fotos de celular, copias xerox).

3. **Multi-stage Docker build:** La separacion builder/runner en el Dockerfile redujo el tamano de la imagen final significativamente.

4. **Tests con mocks:** Los tests unitarios usan mocks efectivos para no depender de Tesseract instalado en CI.

5. **Deskew automatico:** La correccion de rotacion via Hough Lines funciona bien para documentos rotados hasta ±15 grados.

---

## Lo Que Salio Mal

1. **libgl1-mesa-glx deprecado:** En Ubuntu 24.04 / Debian Trixie, el paquete fue renombrado a `libgl1`. Costo 1 hora de debug en CI.

2. **Tiempo de build largo:** La primera build del contenedor backend (con SpaCy, TF, PyTorch) tarda ~45 minutos en la instancia t3.small. Optimizable con cache de capas.

3. **PyMuPDF vs PDFs escaneados:** Los PDFs escaneados no tienen texto nativo, por lo que requieren el fallback a pdf2image + OCR. El manejo de este caso requirio mas logica de la anticipada.

4. **Confianza del OCR en manuscritos:** Para documentos completamente manuscritos (no impresos), la confianza de Tesseract cae a <60%. Esto es una limitacion conocida de Tesseract.

---

## Acciones de Mejora

| Accion | Responsable | Sprint |
|--------|-------------|--------|
| Documentar limitacion de manuscritos en README | Said | Sprint 2 |
| Agregar pre-calentamiento de Docker layer cache en CI | Said | Sprint 3 (DevOps) |
| Investigar EasyOCR como alternativa para manuscritos | Said | Backlog |

---

## Metricas del Sprint

| Metrica | Valor |
|---------|-------|
| Story points completados | 26 |
| Tests escritos | 45 |
| Coverage alcanzado | 83% |
| Bugs encontrados en testing | 3 |
| Bugs resueltos | 3 |
| Tiempo total estimado | 5 dias |
| Tiempo real | 5 dias |

---

## Commits del Sprint

- `chore: initial project setup with full directory structure, Docker, and DB schema` (v0.1.0)
- `feat(ocr): implement OpenCV preprocessing pipeline and Tesseract/PyMuPDF extraction` (v0.2.0)

---

## Demo

Al final del sprint, el sistema puede:
1. Recibir una imagen JPG/PNG de un expediente medico
2. Preprocesarla con OpenCV (deskew, denoise, adaptive threshold)
3. Extraer texto con Tesseract en espanol
4. Retornar texto + confianza + bounding boxes de cada bloque
5. Manejar PDFs nativos con PyMuPDF y PDFs escaneados con OCR fallback

---

*Sprint 1 completado: 7 Febrero 2026*
