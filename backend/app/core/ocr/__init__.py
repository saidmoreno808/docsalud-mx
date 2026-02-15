"""
Modulo OCR y Vision Artificial de DocSalud MX.

Proporciona pipeline completo para extraer texto de imagenes
y PDFs de expedientes clinicos usando OpenCV y Tesseract.
"""

from app.core.ocr.extractor import OCRExtractor
from app.core.ocr.image_handler import ImageHandler
from app.core.ocr.pdf_handler import PDFHandler
from app.core.ocr.preprocessor import ImagePreprocessor
from app.core.ocr.types import OCRResult, PreprocessConfig, TextBlock

__all__ = [
    "ImagePreprocessor",
    "OCRExtractor",
    "ImageHandler",
    "PDFHandler",
    "OCRResult",
    "TextBlock",
    "PreprocessConfig",
]
