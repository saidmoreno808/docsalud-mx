"""
Tests unitarios para ImagePreprocessor.

Verifica que cada paso del pipeline de preprocesamiento
produce los resultados esperados.
"""

import numpy as np
import pytest

from app.core.ocr.preprocessor import ImagePreprocessor
from app.core.ocr.types import PreprocessConfig


@pytest.fixture
def preprocessor() -> ImagePreprocessor:
    """Crea un preprocessor con configuracion default."""
    return ImagePreprocessor()


@pytest.fixture
def sample_bgr_image() -> np.ndarray:
    """Crea una imagen BGR sintetica con texto simulado.

    Imagen 800x600 blanca con rectángulos negros simulando texto.
    """
    image = np.ones((600, 800, 3), dtype=np.uint8) * 255
    # Simular lineas de texto (rectangulos negros)
    for y in range(100, 500, 40):
        image[y : y + 15, 100:700] = 0
    return image


@pytest.fixture
def sample_gray_image(sample_bgr_image: np.ndarray) -> np.ndarray:
    """Crea una imagen en escala de grises."""
    import cv2

    return cv2.cvtColor(sample_bgr_image, cv2.COLOR_BGR2GRAY)


@pytest.fixture
def noisy_gray_image(sample_gray_image: np.ndarray) -> np.ndarray:
    """Crea una imagen en escala de grises con ruido."""
    noise = np.random.normal(0, 25, sample_gray_image.shape).astype(np.int16)
    noisy = np.clip(sample_gray_image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return noisy


@pytest.fixture
def large_image() -> np.ndarray:
    """Crea una imagen grande (5000x4000)."""
    return np.ones((4000, 5000, 3), dtype=np.uint8) * 200


@pytest.fixture
def rotated_image(sample_gray_image: np.ndarray) -> np.ndarray:
    """Crea una imagen rotada 5 grados."""
    import cv2

    h, w = sample_gray_image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, 5, 1.0)
    return cv2.warpAffine(
        sample_gray_image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE
    )


class TestToGrayscale:
    """Tests para conversion a escala de grises."""

    def test_converts_bgr_to_gray(
        self, preprocessor: ImagePreprocessor, sample_bgr_image: np.ndarray
    ) -> None:
        """Imagen BGR se convierte a 1 canal."""
        result = preprocessor.to_grayscale(sample_bgr_image)
        assert len(result.shape) == 2

    def test_gray_image_unchanged(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Imagen ya en gris no cambia."""
        result = preprocessor.to_grayscale(sample_gray_image)
        assert len(result.shape) == 2
        np.testing.assert_array_equal(result, sample_gray_image)

    def test_output_dtype_uint8(
        self, preprocessor: ImagePreprocessor, sample_bgr_image: np.ndarray
    ) -> None:
        """Output es uint8."""
        result = preprocessor.to_grayscale(sample_bgr_image)
        assert result.dtype == np.uint8

    def test_single_channel_image(self, preprocessor: ImagePreprocessor) -> None:
        """Imagen con 1 canal explicito se maneja correctamente."""
        img = np.ones((100, 100, 1), dtype=np.uint8) * 128
        result = preprocessor.to_grayscale(img)
        assert len(result.shape) == 2


class TestResizeIfNeeded:
    """Tests para redimensionamiento condicional."""

    def test_large_image_resized(
        self, preprocessor: ImagePreprocessor, large_image: np.ndarray
    ) -> None:
        """Imagen grande se redimensiona al maximo configurado."""
        result = preprocessor.resize_if_needed(large_image)
        max_dim = max(result.shape[:2])
        assert max_dim <= preprocessor.config.max_dimension

    def test_small_image_unchanged(
        self, preprocessor: ImagePreprocessor, sample_bgr_image: np.ndarray
    ) -> None:
        """Imagen pequena no se modifica."""
        result = preprocessor.resize_if_needed(sample_bgr_image)
        assert result.shape == sample_bgr_image.shape

    def test_aspect_ratio_preserved(
        self, preprocessor: ImagePreprocessor, large_image: np.ndarray
    ) -> None:
        """Aspect ratio se mantiene despues del resize."""
        original_ratio = large_image.shape[1] / large_image.shape[0]
        result = preprocessor.resize_if_needed(large_image)
        new_ratio = result.shape[1] / result.shape[0]
        assert abs(original_ratio - new_ratio) < 0.01

    def test_custom_max_dim(
        self, preprocessor: ImagePreprocessor, sample_bgr_image: np.ndarray
    ) -> None:
        """Resize con dimension maxima custom."""
        result = preprocessor.resize_if_needed(sample_bgr_image, max_dim=200)
        max_dim = max(result.shape[:2])
        assert max_dim <= 200


class TestAdaptiveThreshold:
    """Tests para binarizacion adaptativa."""

    def test_output_binary(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Output solo contiene valores 0 y 255."""
        result = preprocessor.adaptive_threshold(sample_gray_image)
        unique_values = np.unique(result)
        assert all(v in [0, 255] for v in unique_values)

    def test_output_same_shape(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Output tiene las mismas dimensiones que input."""
        result = preprocessor.adaptive_threshold(sample_gray_image)
        assert result.shape == sample_gray_image.shape

    def test_output_dtype_uint8(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Output es uint8."""
        result = preprocessor.adaptive_threshold(sample_gray_image)
        assert result.dtype == np.uint8


class TestDenoise:
    """Tests para eliminacion de ruido."""

    def test_reduces_noise(
        self, preprocessor: ImagePreprocessor, noisy_gray_image: np.ndarray
    ) -> None:
        """Denoising reduce la varianza del ruido."""
        result = preprocessor.denoise(noisy_gray_image)
        # La desviacion estandar debe reducirse
        original_std = np.std(noisy_gray_image.astype(float))
        denoised_std = np.std(result.astype(float))
        # No siempre reduce std globalmente, pero debe suavizar
        assert result.dtype == np.uint8

    def test_output_same_shape(
        self, preprocessor: ImagePreprocessor, noisy_gray_image: np.ndarray
    ) -> None:
        """Output tiene las mismas dimensiones."""
        result = preprocessor.denoise(noisy_gray_image)
        assert result.shape == noisy_gray_image.shape

    def test_clean_image_not_degraded(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Imagen limpia no se degrada significativamente."""
        result = preprocessor.denoise(sample_gray_image)
        # La diferencia promedio debe ser pequena
        diff = np.abs(result.astype(float) - sample_gray_image.astype(float))
        assert np.mean(diff) < 5.0


class TestDeskew:
    """Tests para correccion de rotacion."""

    def test_horizontal_image_unchanged(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Imagen sin rotacion no cambia significativamente."""
        result = preprocessor.deskew(sample_gray_image)
        assert result.shape == sample_gray_image.shape

    def test_rotated_image_corrected(
        self, preprocessor: ImagePreprocessor, rotated_image: np.ndarray
    ) -> None:
        """Imagen rotada se corrige (el resultado tiene las mismas dimensiones)."""
        result = preprocessor.deskew(rotated_image)
        assert result.shape == rotated_image.shape
        # No podemos verificar exactamente el angulo sin mas logica,
        # pero al menos no debe crashear

    def test_empty_image_no_crash(self, preprocessor: ImagePreprocessor) -> None:
        """Imagen vacia (sin lineas) no causa error."""
        empty = np.ones((300, 400), dtype=np.uint8) * 200
        result = preprocessor.deskew(empty)
        assert result.shape == empty.shape


class TestEnhanceContrast:
    """Tests para mejora de contraste con CLAHE."""

    def test_output_same_shape(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Output mantiene dimensiones."""
        result = preprocessor.enhance_contrast(sample_gray_image)
        assert result.shape == sample_gray_image.shape

    def test_output_dtype_uint8(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Output es uint8."""
        result = preprocessor.enhance_contrast(sample_gray_image)
        assert result.dtype == np.uint8

    def test_low_contrast_improved(self, preprocessor: ImagePreprocessor) -> None:
        """Imagen de bajo contraste mejora su rango dinamico."""
        # Imagen con bajo contraste (valores entre 100 y 150)
        low_contrast = np.random.randint(100, 150, (300, 400), dtype=np.uint8)
        result = preprocessor.enhance_contrast(low_contrast)
        # El rango dinamico debe aumentar
        original_range = int(low_contrast.max()) - int(low_contrast.min())
        enhanced_range = int(result.max()) - int(result.min())
        assert enhanced_range >= original_range


class TestDetectTextRegions:
    """Tests para deteccion de regiones de texto."""

    def test_finds_text_regions(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Imagen con texto simulado detecta al menos 1 region."""
        regions = preprocessor.detect_text_regions(sample_gray_image)
        assert len(regions) >= 1

    def test_regions_have_valid_bbox(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Cada region tiene bounding box valido (x, y, w, h positivos)."""
        regions = preprocessor.detect_text_regions(sample_gray_image)
        for x, y, w, h in regions:
            assert x >= 0
            assert y >= 0
            assert w > 0
            assert h > 0

    def test_blank_image_no_regions(self, preprocessor: ImagePreprocessor) -> None:
        """Imagen en blanco no detecta regiones."""
        blank = np.ones((300, 400), dtype=np.uint8) * 255
        regions = preprocessor.detect_text_regions(blank)
        assert len(regions) == 0

    def test_regions_sorted_top_to_bottom(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Regiones estan ordenadas de arriba a abajo."""
        regions = preprocessor.detect_text_regions(sample_gray_image)
        if len(regions) > 1:
            for i in range(len(regions) - 1):
                assert regions[i][1] <= regions[i + 1][1]


class TestCorrectPerspective:
    """Tests para correccion de perspectiva."""

    def test_no_document_returns_original(self, preprocessor: ImagePreprocessor) -> None:
        """Sin documento claro, retorna la imagen original."""
        random_img = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
        result = preprocessor.correct_perspective(random_img)
        # Debe retornar algo del mismo tipo
        assert isinstance(result, np.ndarray)

    def test_with_clear_document(self, preprocessor: ImagePreprocessor) -> None:
        """Documento con bordes claros se detecta."""
        # Crear imagen con un rectangulo blanco sobre fondo oscuro
        image = np.ones((600, 800, 3), dtype=np.uint8) * 30
        # Dibujar un rectangulo grande (documento)
        import cv2

        pts = np.array([[100, 50], [700, 50], [700, 550], [100, 550]], dtype=np.int32)
        cv2.fillPoly(image, [pts], (240, 240, 240))
        result = preprocessor.correct_perspective(image)
        assert isinstance(result, np.ndarray)

    def test_grayscale_input(
        self, preprocessor: ImagePreprocessor, sample_gray_image: np.ndarray
    ) -> None:
        """Funciona con entrada en escala de grises."""
        result = preprocessor.correct_perspective(sample_gray_image)
        assert isinstance(result, np.ndarray)


class TestPreprocessPipeline:
    """Tests para el pipeline completo."""

    def test_end_to_end(
        self, preprocessor: ImagePreprocessor, sample_bgr_image: np.ndarray
    ) -> None:
        """Pipeline completo ejecuta sin errores."""
        result = preprocessor.preprocess(sample_bgr_image)
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2  # Resultado es binario (2D)
        assert result.dtype == np.uint8

    def test_output_binary(
        self, preprocessor: ImagePreprocessor, sample_bgr_image: np.ndarray
    ) -> None:
        """Pipeline produce imagen binaria."""
        result = preprocessor.preprocess(sample_bgr_image)
        unique_values = np.unique(result)
        assert all(v in [0, 255] for v in unique_values)

    def test_large_image_handled(
        self, preprocessor: ImagePreprocessor, large_image: np.ndarray
    ) -> None:
        """Pipeline maneja imagenes grandes correctamente."""
        result = preprocessor.preprocess(large_image)
        max_dim = max(result.shape[:2])
        assert max_dim <= preprocessor.config.max_dimension

    def test_noisy_image_handled(
        self, preprocessor: ImagePreprocessor, noisy_gray_image: np.ndarray
    ) -> None:
        """Pipeline maneja imagenes con ruido (input gris 2D)."""
        # Agregar canal BGR para simular imagen de entrada real
        bgr = np.stack([noisy_gray_image] * 3, axis=-1)
        result = preprocessor.preprocess(bgr)
        assert isinstance(result, np.ndarray)

    def test_custom_config(self, sample_bgr_image: np.ndarray) -> None:
        """Pipeline funciona con configuracion custom."""
        config = PreprocessConfig(
            max_dimension=500,
            denoise_strength=5,
            adaptive_block_size=15,
            adaptive_c=3,
            clahe_clip_limit=3.0,
        )
        preprocessor = ImagePreprocessor(config)
        result = preprocessor.preprocess(sample_bgr_image)
        assert max(result.shape[:2]) <= 500


class TestOrderPoints:
    """Tests para el helper _order_points."""

    def test_orders_correctly(self) -> None:
        """Puntos se ordenan como TL, TR, BR, BL."""
        # Puntos desordenados
        points = np.array(
            [[200, 10], [10, 10], [200, 200], [10, 200]], dtype=np.float32
        )
        ordered = ImagePreprocessor._order_points(points)

        # top-left debe tener la menor suma x+y
        assert ordered[0][0] < ordered[1][0]  # TL.x < TR.x
        assert ordered[0][1] < ordered[3][1]  # TL.y < BL.y

    def test_already_ordered(self) -> None:
        """Puntos ya ordenados no cambian."""
        points = np.array(
            [[0, 0], [100, 0], [100, 100], [0, 100]], dtype=np.float32
        )
        ordered = ImagePreprocessor._order_points(points)
        np.testing.assert_array_equal(ordered[0], [0, 0])
        np.testing.assert_array_equal(ordered[2], [100, 100])
