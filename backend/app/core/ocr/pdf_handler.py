"""
Manejo especifico de PDFs para el pipeline OCR.

Soporta PDFs nativos (con texto embebido) y PDFs escaneados
(imagenes sin texto). Usa PyMuPDF para extraccion directa
y pdf2image + Tesseract como fallback para escaneados.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_PDF_SIZE_MB = 10
MAX_PDF_PAGES = 50


class PDFHandler:
    """Manejo de carga y extraccion de PDFs.

    Distingue entre PDFs con texto nativo (extraccion directa)
    y PDFs escaneados (requieren OCR).
    """

    def extract_text_native(self, pdf_path: str | Path) -> str | None:
        """Intenta extraer texto directamente del PDF (sin OCR).

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            Texto extraido si el PDF tiene texto embebido, None si
            es un PDF escaneado (pura imagen).
        """
        pdf_path = Path(pdf_path)
        self._validate_pdf(pdf_path)

        doc = fitz.open(str(pdf_path))
        try:
            all_text: list[str] = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    all_text.append(text.strip())

            if not all_text:
                logger.debug("pdf_no_native_text", path=str(pdf_path))
                return None

            combined = "\n\n".join(all_text)
            logger.debug(
                "pdf_native_text_extracted",
                path=str(pdf_path),
                pages=len(doc),
                chars=len(combined),
            )
            return combined
        finally:
            doc.close()

    def pdf_to_images(self, pdf_path: str | Path, dpi: int = 300) -> list[np.ndarray]:
        """Convierte paginas del PDF a imagenes numpy.

        Usa PyMuPDF para renderizar cada pagina a la resolucion
        especificada.

        Args:
            pdf_path: Ruta al archivo PDF.
            dpi: Resolucion de renderizado en DPI.

        Returns:
            Lista de imagenes numpy array BGR, una por pagina.
        """
        pdf_path = Path(pdf_path)
        self._validate_pdf(pdf_path)

        doc = fitz.open(str(pdf_path))
        images: list[np.ndarray] = []

        try:
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)

            for page_num, page in enumerate(doc):
                if page_num >= MAX_PDF_PAGES:
                    logger.warning(
                        "pdf_page_limit_reached",
                        max_pages=MAX_PDF_PAGES,
                        total_pages=len(doc),
                    )
                    break

                pix = page.get_pixmap(matrix=matrix)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                np_img = np.array(img)
                # PIL produce RGB, OpenCV espera BGR
                bgr_img = np_img[:, :, ::-1].copy()
                images.append(bgr_img)

            logger.debug("pdf_to_images_complete", pages=len(images), dpi=dpi)
            return images
        finally:
            doc.close()

    def get_page_count(self, pdf_path: str | Path) -> int:
        """Obtiene el numero de paginas del PDF.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            Numero de paginas.
        """
        pdf_path = Path(pdf_path)
        self._validate_pdf(pdf_path)

        doc = fitz.open(str(pdf_path))
        try:
            return len(doc)
        finally:
            doc.close()

    def has_native_text(self, pdf_path: str | Path) -> bool:
        """Verifica si el PDF contiene texto embebido.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            True si al menos una pagina tiene texto extractable.
        """
        text = self.extract_text_native(pdf_path)
        return text is not None and len(text.strip()) > 0

    @staticmethod
    def is_pdf(filename: str) -> bool:
        """Verifica si el archivo tiene extension PDF.

        Args:
            filename: Nombre del archivo.

        Returns:
            True si es un PDF.
        """
        return Path(filename).suffix.lower() == ".pdf"

    def _validate_pdf(self, pdf_path: Path) -> None:
        """Valida que el archivo PDF existe y no excede el limite de tamano.

        Args:
            pdf_path: Ruta al archivo PDF.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si no es un PDF o excede el tamano maximo.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"El archivo no es un PDF: {pdf_path}")

        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_PDF_SIZE_MB:
            raise ValueError(
                f"PDF excede el limite de {MAX_PDF_SIZE_MB}MB: {file_size_mb:.1f}MB"
            )
