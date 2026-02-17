"""
Tests unitarios para OCRExtractor.

Usa mocks para Tesseract y PyMuPDF para permitir tests
sin dependencias de sistema instaladas.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.core.ocr.extractor import OCRExtractor
from app.core.ocr.image_handler import ImageHandler
from app.core.ocr.pdf_handler import PDFHandler
from app.core.ocr.types import OCRResult, PreprocessConfig, TextBlock


@pytest.fixture
def extractor() -> OCRExtractor:
    """Crea un OCRExtractor con config default."""
    return OCRExtractor(tesseract_lang="spa")


@pytest.fixture
def sample_image() -> np.ndarray:
    """Imagen sintetica 400x600 BGR con texto simulado."""
    image = np.ones((400, 600, 3), dtype=np.uint8) * 255
    for y in range(80, 350, 30):
        image[y : y + 12, 80:520] = 0
    return image


@pytest.fixture
def mock_tesseract_data() -> dict:
    """Datos de salida simulados de pytesseract.image_to_data."""
    return {
        "level": [1, 2, 3, 4, 5, 5, 5],
        "page_num": [1, 1, 1, 1, 1, 1, 1],
        "block_num": [0, 1, 1, 1, 1, 1, 1],
        "par_num": [0, 1, 1, 1, 1, 1, 1],
        "line_num": [0, 0, 1, 1, 1, 1, 1],
        "word_num": [0, 0, 0, 1, 1, 2, 3],
        "left": [0, 50, 50, 50, 50, 150, 280],
        "top": [0, 30, 30, 30, 30, 30, 30],
        "width": [600, 500, 500, 90, 90, 120, 100],
        "height": [400, 350, 20, 20, 20, 20, 20],
        "conf": [-1, -1, -1, 92.5, 92.5, 88.3, 95.1],
        "text": ["", "", "", "Paciente:", "Paciente:", "Juan", "Perez"],
    }


class TestExtractFromImage:
    """Tests para extraccion OCR de imagenes."""

    @patch("app.core.ocr.extractor.pytesseract")
    def test_returns_ocr_result(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """Extraccion retorna un OCRResult valido."""
        mock_pytesseract.image_to_string.return_value = "Paciente: Juan Perez"
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(extractor.image_handler, "load_from_path", return_value=sample_image):
            result = extractor.extract_from_image("test.jpg")

        assert isinstance(result, OCRResult)
        assert result.text == "Paciente: Juan Perez"
        assert result.page_count == 1
        assert result.processing_time_ms >= 0

    @patch("app.core.ocr.extractor.pytesseract")
    def test_high_confidence_no_warnings(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """Extraccion con alta confianza no genera warnings."""
        mock_pytesseract.image_to_string.return_value = "Texto claro"
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(extractor.image_handler, "load_from_path", return_value=sample_image):
            result = extractor.extract_from_image("test.jpg")

        assert len(result.warnings) == 0

    @patch("app.core.ocr.extractor.pytesseract")
    def test_low_confidence_generates_warning(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
    ) -> None:
        """Confianza baja genera warning."""
        low_conf_data = {
            "level": [5, 5],
            "page_num": [1, 1],
            "block_num": [1, 1],
            "par_num": [1, 1],
            "line_num": [1, 1],
            "word_num": [1, 2],
            "left": [50, 150],
            "top": [30, 30],
            "width": [90, 120],
            "height": [20, 20],
            "conf": [25.0, 30.0],
            "text": ["algo", "borroso"],
        }
        mock_pytesseract.image_to_string.return_value = "algo borroso"
        mock_pytesseract.image_to_data.return_value = low_conf_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(extractor.image_handler, "load_from_path", return_value=sample_image):
            result = extractor.extract_from_image("test.jpg")

        assert len(result.warnings) > 0
        assert any("baja" in w.lower() for w in result.warnings)

    @patch("app.core.ocr.extractor.pytesseract")
    def test_blocks_have_valid_bbox(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """Bloques extraidos tienen bounding box valido."""
        mock_pytesseract.image_to_string.return_value = "Texto"
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(extractor.image_handler, "load_from_path", return_value=sample_image):
            result = extractor.extract_from_image("test.jpg")

        for block in result.blocks:
            x, y, w, h = block.bbox
            assert w >= 0
            assert h >= 0


class TestExtractFromPdf:
    """Tests para extraccion OCR de PDFs."""

    @patch("app.core.ocr.extractor.pytesseract")
    def test_native_pdf_no_ocr(
        self, mock_pytesseract: MagicMock, extractor: OCRExtractor
    ) -> None:
        """PDF con texto nativo no necesita OCR."""
        native_text = "Receta medica completa con texto nativo suficiente para extraccion directa."

        with patch.object(
            extractor.pdf_handler, "extract_text_native", return_value=native_text
        ), patch.object(extractor.pdf_handler, "get_page_count", return_value=1):
            result = extractor.extract_from_pdf("test.pdf")

        assert result.text == native_text
        assert result.confidence == 99.0
        assert result.page_count == 1
        # Tesseract no debe haberse llamado
        mock_pytesseract.image_to_string.assert_not_called()

    @patch("app.core.ocr.extractor.pytesseract")
    def test_scanned_pdf_uses_ocr(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """PDF escaneado usa OCR como fallback."""
        mock_pytesseract.image_to_string.return_value = "Texto OCR"
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(
            extractor.pdf_handler, "extract_text_native", return_value=None
        ), patch.object(
            extractor.pdf_handler, "pdf_to_images", return_value=[sample_image]
        ):
            result = extractor.extract_from_pdf("scanned.pdf")

        assert result.text == "Texto OCR"
        assert any("escaneado" in w.lower() for w in result.warnings)

    @patch("app.core.ocr.extractor.pytesseract")
    def test_multi_page_pdf(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """PDF con multiples paginas combina texto."""
        mock_pytesseract.image_to_string.side_effect = ["Pagina 1", "Pagina 2"]
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(
            extractor.pdf_handler, "extract_text_native", return_value=None
        ), patch.object(
            extractor.pdf_handler,
            "pdf_to_images",
            return_value=[sample_image, sample_image],
        ):
            result = extractor.extract_from_pdf("multi.pdf")

        assert "Pagina 1" in result.text
        assert "Pagina 2" in result.text
        assert result.page_count == 2


class TestExtractFromNumpy:
    """Tests para extraccion directa desde numpy array."""

    @patch("app.core.ocr.extractor.pytesseract")
    def test_returns_valid_result(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """Extraccion desde numpy retorna OCRResult valido."""
        mock_pytesseract.image_to_string.return_value = "Texto directo"
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        result = extractor.extract_from_numpy(sample_image)

        assert isinstance(result, OCRResult)
        assert result.text == "Texto directo"
        assert result.page_count == 1


class TestExtractAuto:
    """Tests para deteccion automatica de tipo de archivo."""

    @patch("app.core.ocr.extractor.pytesseract")
    def test_auto_detects_image(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """Detecta imagen y usa extract_from_image."""
        mock_pytesseract.image_to_string.return_value = "Texto"
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(extractor.image_handler, "load_from_path", return_value=sample_image):
            result = extractor.extract_auto("foto.jpg")

        assert isinstance(result, OCRResult)

    def test_auto_detects_pdf(self, extractor: OCRExtractor) -> None:
        """Detecta PDF y usa extract_from_pdf."""
        native_text = "Texto nativo de PDF con contenido suficiente para pasar el threshold minimo."

        with patch.object(
            extractor.pdf_handler, "extract_text_native", return_value=native_text
        ), patch.object(extractor.pdf_handler, "get_page_count", return_value=1), patch.object(
            extractor.pdf_handler, "_validate_pdf"
        ):
            result = extractor.extract_auto("documento.pdf")

        assert isinstance(result, OCRResult)

    def test_auto_rejects_unsupported(self, extractor: OCRExtractor) -> None:
        """Formato no soportado lanza ValueError."""
        with pytest.raises(ValueError, match="no soportado"):
            extractor.extract_auto("archivo.docx")


class TestExtractWithLayout:
    """Tests para extraccion con informacion de layout."""

    @patch("app.core.ocr.extractor.pytesseract")
    def test_returns_text_blocks(
        self,
        mock_pytesseract: MagicMock,
        extractor: OCRExtractor,
        sample_image: np.ndarray,
        mock_tesseract_data: dict,
    ) -> None:
        """Extraccion con layout retorna lista de TextBlock."""
        mock_pytesseract.image_to_data.return_value = mock_tesseract_data
        mock_pytesseract.Output.DICT = "dict"

        with patch.object(extractor.image_handler, "load_from_path", return_value=sample_image):
            blocks = extractor.extract_with_layout("test.jpg")

        assert isinstance(blocks, list)
        for block in blocks:
            assert isinstance(block, TextBlock)
            assert block.text
            assert block.confidence >= 0


class TestBuildBlocksFromData:
    """Tests para el metodo estatico de construccion de bloques."""

    def test_filters_empty_entries(self, mock_tesseract_data: dict) -> None:
        """Entradas vacias (conf=-1 o texto vacio) se filtran."""
        blocks, confidence = OCRExtractor._build_blocks_from_data(mock_tesseract_data)
        for block in blocks:
            assert block.text.strip() != ""

    def test_groups_by_block_num(self, mock_tesseract_data: dict) -> None:
        """Palabras se agrupan por block_num."""
        blocks, _ = OCRExtractor._build_blocks_from_data(mock_tesseract_data)
        # Todos los datos de mock estan en block_num=1
        assert len(blocks) >= 1

    def test_confidence_is_average(self) -> None:
        """Confianza promedio se calcula correctamente."""
        data = {
            "level": [5, 5],
            "page_num": [1, 1],
            "block_num": [1, 1],
            "par_num": [1, 1],
            "line_num": [1, 1],
            "word_num": [1, 2],
            "left": [50, 150],
            "top": [30, 30],
            "width": [90, 120],
            "height": [20, 20],
            "conf": [80.0, 90.0],
            "text": ["Hola", "Mundo"],
        }
        _, confidence = OCRExtractor._build_blocks_from_data(data)
        assert abs(confidence - 85.0) < 0.1

    def test_empty_data_returns_empty(self) -> None:
        """Datos vacios retornan lista vacia y confianza 0."""
        data = {
            "level": [],
            "page_num": [],
            "block_num": [],
            "par_num": [],
            "line_num": [],
            "word_num": [],
            "left": [],
            "top": [],
            "width": [],
            "height": [],
            "conf": [],
            "text": [],
        }
        blocks, confidence = OCRExtractor._build_blocks_from_data(data)
        assert blocks == []
        assert confidence == 0.0


class TestImageHandler:
    """Tests para ImageHandler."""

    def test_is_supported_valid_extensions(self) -> None:
        """Extensiones validas son reconocidas."""
        assert ImageHandler.is_supported("foto.jpg")
        assert ImageHandler.is_supported("scan.png")
        assert ImageHandler.is_supported("doc.tiff")
        assert ImageHandler.is_supported("image.JPEG")

    def test_is_supported_invalid_extensions(self) -> None:
        """Extensiones invalidas son rechazadas."""
        assert not ImageHandler.is_supported("doc.pdf")
        assert not ImageHandler.is_supported("file.docx")
        assert not ImageHandler.is_supported("data.csv")

    def test_load_from_bytes_empty_raises(self) -> None:
        """Bytes vacios lanzan ValueError."""
        handler = ImageHandler()
        with pytest.raises(ValueError, match="vacios"):
            handler.load_from_bytes(b"")

    def test_load_from_path_not_found(self) -> None:
        """Archivo inexistente lanza FileNotFoundError."""
        handler = ImageHandler()
        with pytest.raises(FileNotFoundError):
            handler.load_from_path("/no/existe/imagen.jpg")

    def test_load_from_path_unsupported_format(self, tmp_path: Path) -> None:
        """Formato no soportado lanza ValueError."""
        handler = ImageHandler()
        fake_file = tmp_path / "test.docx"
        fake_file.write_bytes(b"not an image")
        with pytest.raises(ValueError, match="no soportado"):
            handler.load_from_path(str(fake_file))

    def test_load_from_pil(self) -> None:
        """Carga desde imagen PIL funciona."""
        from PIL import Image

        handler = ImageHandler()
        pil_img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        result = handler.load_from_pil(pil_img)
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 3)

    def test_load_from_pil_grayscale(self) -> None:
        """Carga desde imagen PIL en escala de grises."""
        from PIL import Image

        handler = ImageHandler()
        pil_img = Image.new("L", (100, 100), color=128)
        result = handler.load_from_pil(pil_img)
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2


class TestPDFHandler:
    """Tests para PDFHandler."""

    def test_is_pdf_valid(self) -> None:
        """Archivos .pdf son reconocidos."""
        assert PDFHandler.is_pdf("documento.pdf")
        assert PDFHandler.is_pdf("SCAN.PDF")

    def test_is_pdf_invalid(self) -> None:
        """Archivos no-pdf son rechazados."""
        assert not PDFHandler.is_pdf("imagen.jpg")
        assert not PDFHandler.is_pdf("doc.docx")

    def test_validate_pdf_not_found(self) -> None:
        """PDF inexistente lanza FileNotFoundError."""
        handler = PDFHandler()
        with pytest.raises(FileNotFoundError):
            handler._validate_pdf(Path("/no/existe.pdf"))

    def test_validate_pdf_wrong_extension(self, tmp_path: Path) -> None:
        """Archivo sin extension .pdf lanza ValueError."""
        handler = PDFHandler()
        fake_file = tmp_path / "test.txt"
        fake_file.write_bytes(b"not a pdf")
        with pytest.raises(ValueError, match="no es un PDF"):
            handler._validate_pdf(fake_file)
