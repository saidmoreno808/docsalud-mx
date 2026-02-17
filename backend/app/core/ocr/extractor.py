"""
Motor de OCR que combina Tesseract y PyMuPDF.

Tesseract para imagenes y PDFs escaneados.
PyMuPDF para PDFs con texto nativo (sin necesidad de OCR).
"""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np
import pytesseract

from app.config import settings
from app.core.ocr.image_handler import ImageHandler
from app.core.ocr.pdf_handler import PDFHandler
from app.core.ocr.preprocessor import ImagePreprocessor
from app.core.ocr.types import OCRResult, PreprocessConfig, TextBlock
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OCRExtractor:
    """Extractor de texto mediante OCR.

    Combina preprocesamiento OpenCV con Tesseract para imagenes
    y PyMuPDF para PDFs nativos, seleccionando automaticamente
    la mejor estrategia segun el tipo de archivo.

    Args:
        config: Configuracion de preprocesamiento.
        tesseract_lang: Idioma de Tesseract (default: 'spa' para espanol).
    """

    def __init__(
        self,
        config: PreprocessConfig | None = None,
        tesseract_lang: str | None = None,
    ) -> None:
        self.preprocessor = ImagePreprocessor(config)
        self.image_handler = ImageHandler()
        self.pdf_handler = PDFHandler()
        self.tesseract_lang = tesseract_lang or settings.tesseract_lang

        # Configurar ruta de Tesseract si se especifica
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    def extract_from_image(self, image_path: str | Path) -> OCRResult:
        """Extrae texto de una imagen.

        Pipeline:
            1. Carga imagen con ImageHandler
            2. Preprocesa con ImagePreprocessor
            3. Ejecuta Tesseract con config optimizada
            4. Obtiene texto + confianza por palabra
            5. Retorna OCRResult completo

        Args:
            image_path: Ruta al archivo de imagen.

        Returns:
            OCRResult con texto, confianza, bloques y warnings.
        """
        start_time = time.time()
        warnings: list[str] = []

        logger.info("ocr_extract_image_start", path=str(image_path))

        # Cargar imagen
        image = self.image_handler.load_from_path(image_path)

        # Preprocesar
        preprocessed = self.preprocessor.preprocess(image)

        # OCR con Tesseract
        tesseract_config = f"--oem 3 --psm 6 -l {self.tesseract_lang}"

        # Obtener texto completo
        text = pytesseract.image_to_string(preprocessed, config=tesseract_config)

        # Obtener datos detallados por palabra
        data = pytesseract.image_to_data(
            preprocessed, config=tesseract_config, output_type=pytesseract.Output.DICT
        )

        # Construir bloques y calcular confianza
        blocks, avg_confidence = self._build_blocks_from_data(data, page=0)

        # Generar warnings
        if avg_confidence < 50:
            warnings.append(
                f"Confianza baja ({avg_confidence:.1f}%). "
                "Considere mejorar la calidad de la imagen."
            )
        if avg_confidence < 30:
            warnings.append(
                "Confianza muy baja. El texto extraido puede contener errores significativos."
            )

        processing_time_ms = int((time.time() - start_time) * 1000)

        result = OCRResult(
            text=text.strip(),
            confidence=avg_confidence,
            page_count=1,
            blocks=blocks,
            processing_time_ms=processing_time_ms,
            warnings=warnings,
        )

        logger.info(
            "ocr_extract_image_complete",
            path=str(image_path),
            confidence=avg_confidence,
            chars=len(result.text),
            time_ms=processing_time_ms,
        )

        return result

    def extract_from_pdf(self, pdf_path: str | Path) -> OCRResult:
        """Extrae texto de PDF.

        Estrategia:
            1. Intenta extraccion directa con PyMuPDF (PDFs nativos)
            2. Si no hay texto (PDF escaneado), convierte a imagenes
            3. Aplica OCR a cada pagina
            4. Combina resultados

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            OCRResult con texto combinado de todas las paginas.
        """
        start_time = time.time()
        warnings: list[str] = []

        logger.info("ocr_extract_pdf_start", path=str(pdf_path))

        # Intentar extraccion nativa
        native_text = self.pdf_handler.extract_text_native(pdf_path)

        if native_text and len(native_text.strip()) > 50:
            # PDF con texto nativo — no necesita OCR
            page_count = self.pdf_handler.get_page_count(pdf_path)
            processing_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "ocr_pdf_native_extraction",
                path=str(pdf_path),
                pages=page_count,
                chars=len(native_text),
            )

            return OCRResult(
                text=native_text,
                confidence=99.0,
                page_count=page_count,
                blocks=[
                    TextBlock(
                        text=native_text,
                        confidence=99.0,
                        bbox=(0, 0, 0, 0),
                        page=0,
                        block_type="paragraph",
                    )
                ],
                processing_time_ms=processing_time_ms,
                warnings=[],
            )

        # PDF escaneado — necesita OCR por pagina
        logger.debug("pdf_scanned_detected_using_ocr", path=str(pdf_path))
        warnings.append("PDF escaneado detectado. Se uso OCR para extraccion.")

        page_images = self.pdf_handler.pdf_to_images(pdf_path)
        all_text: list[str] = []
        all_blocks: list[TextBlock] = []
        total_confidence = 0.0
        pages_with_text = 0

        tesseract_config = f"--oem 3 --psm 6 -l {self.tesseract_lang}"

        for page_num, page_image in enumerate(page_images):
            # Preprocesar cada pagina
            preprocessed = self.preprocessor.preprocess(page_image)

            # OCR
            text = pytesseract.image_to_string(preprocessed, config=tesseract_config)
            data = pytesseract.image_to_data(
                preprocessed, config=tesseract_config, output_type=pytesseract.Output.DICT
            )

            blocks, page_confidence = self._build_blocks_from_data(data, page=page_num)

            if text.strip():
                all_text.append(text.strip())
                all_blocks.extend(blocks)
                total_confidence += page_confidence
                pages_with_text += 1

        combined_text = "\n\n".join(all_text)
        avg_confidence = total_confidence / max(pages_with_text, 1)

        if avg_confidence < 50:
            warnings.append(
                f"Confianza baja ({avg_confidence:.1f}%). "
                "La calidad del escaneo puede ser insuficiente."
            )

        processing_time_ms = int((time.time() - start_time) * 1000)

        result = OCRResult(
            text=combined_text,
            confidence=avg_confidence,
            page_count=len(page_images),
            blocks=all_blocks,
            processing_time_ms=processing_time_ms,
            warnings=warnings,
        )

        logger.info(
            "ocr_extract_pdf_complete",
            path=str(pdf_path),
            pages=len(page_images),
            confidence=avg_confidence,
            chars=len(combined_text),
            time_ms=processing_time_ms,
        )

        return result

    def extract_from_numpy(self, image: np.ndarray) -> OCRResult:
        """Extrae texto de un numpy array directamente.

        Util para imagenes ya cargadas en memoria (ej: desde un upload
        HTTP o procesamiento previo).

        Args:
            image: Imagen como numpy array BGR o escala de grises.

        Returns:
            OCRResult con texto extraido.
        """
        start_time = time.time()
        warnings: list[str] = []

        preprocessed = self.preprocessor.preprocess(image)

        tesseract_config = f"--oem 3 --psm 6 -l {self.tesseract_lang}"
        text = pytesseract.image_to_string(preprocessed, config=tesseract_config)
        data = pytesseract.image_to_data(
            preprocessed, config=tesseract_config, output_type=pytesseract.Output.DICT
        )

        blocks, avg_confidence = self._build_blocks_from_data(data, page=0)

        if avg_confidence < 50:
            warnings.append(f"Confianza baja ({avg_confidence:.1f}%).")

        processing_time_ms = int((time.time() - start_time) * 1000)

        return OCRResult(
            text=text.strip(),
            confidence=avg_confidence,
            page_count=1,
            blocks=blocks,
            processing_time_ms=processing_time_ms,
            warnings=warnings,
        )

    def extract_with_layout(self, image_path: str | Path) -> list[TextBlock]:
        """Extraccion con informacion de layout detallada.

        Usa Tesseract con output_type=dict para obtener posiciones.
        Agrupa palabras en bloques y lineas para entender la estructura.

        Args:
            image_path: Ruta al archivo de imagen.

        Returns:
            Lista de TextBlock con posicion y tipo de bloque.
        """
        image = self.image_handler.load_from_path(image_path)
        preprocessed = self.preprocessor.preprocess(image)

        tesseract_config = f"--oem 3 --psm 6 -l {self.tesseract_lang}"
        data = pytesseract.image_to_data(
            preprocessed, config=tesseract_config, output_type=pytesseract.Output.DICT
        )

        blocks, _ = self._build_blocks_from_data(data, page=0)
        return blocks

    def extract_auto(self, file_path: str | Path) -> OCRResult:
        """Detecta automaticamente el tipo de archivo y extrae texto.

        Args:
            file_path: Ruta al archivo (imagen o PDF).

        Returns:
            OCRResult con texto extraido.

        Raises:
            ValueError: Si el formato no es soportado.
        """
        file_path = Path(file_path)

        if self.pdf_handler.is_pdf(str(file_path)):
            return self.extract_from_pdf(file_path)
        elif self.image_handler.is_supported(str(file_path)):
            return self.extract_from_image(file_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_path.suffix}")

    @staticmethod
    def _build_blocks_from_data(
        data: dict, page: int = 0
    ) -> tuple[list[TextBlock], float]:
        """Construye TextBlocks a partir de los datos de Tesseract.

        Agrupa palabras por bloque (block_num) para crear bloques
        de texto coherentes con posicion.

        Args:
            data: Diccionario de salida de pytesseract.image_to_data.
            page: Numero de pagina.

        Returns:
            Tupla de (lista de TextBlock, confianza promedio).
        """
        blocks: dict[int, list[dict]] = {}
        confidences: list[float] = []

        n_items = len(data["text"])

        for i in range(n_items):
            text = data["text"][i].strip()
            conf = float(data["conf"][i])

            # Tesseract retorna -1 de confianza para elementos vacios
            if conf < 0 or not text:
                continue

            confidences.append(conf)
            block_num = data["block_num"][i]

            if block_num not in blocks:
                blocks[block_num] = []

            blocks[block_num].append(
                {
                    "text": text,
                    "conf": conf,
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                }
            )

        # Construir TextBlocks
        text_blocks: list[TextBlock] = []
        for block_num in sorted(blocks.keys()):
            words = blocks[block_num]
            block_text = " ".join(w["text"] for w in words)
            block_conf = sum(w["conf"] for w in words) / len(words)

            # Bounding box del bloque completo
            min_x = min(w["left"] for w in words)
            min_y = min(w["top"] for w in words)
            max_x = max(w["left"] + w["width"] for w in words)
            max_y = max(w["top"] + w["height"] for w in words)

            text_blocks.append(
                TextBlock(
                    text=block_text,
                    confidence=block_conf,
                    bbox=(min_x, min_y, max_x - min_x, max_y - min_y),
                    page=page,
                    block_type="paragraph",
                )
            )

        avg_confidence = sum(confidences) / max(len(confidences), 1)

        return text_blocks, avg_confidence
