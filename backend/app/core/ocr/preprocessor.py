"""
Modulo de preprocesamiento de imagenes para OCR.

Usa OpenCV para mejorar la calidad de imagenes antes de OCR.
Optimizado para documentos medicos escaneados y fotos de celular.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.core.ocr.types import PreprocessConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ImagePreprocessor:
    """Pipeline de preprocesamiento de imagenes para OCR medico.

    Aplica una serie de transformaciones OpenCV para maximizar
    la calidad del texto antes de enviarlo al motor OCR.

    Args:
        config: Configuracion del pipeline de preprocesamiento.
    """

    def __init__(self, config: PreprocessConfig | None = None) -> None:
        self.config = config or PreprocessConfig()

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Pipeline completo de preprocesamiento.

        Pasos:
            1. Resize si es muy grande (max 3000px lado largo)
            2. Convertir a escala de grises
            3. Mejora de contraste con CLAHE
            4. Eliminacion de ruido (denoising)
            5. Correccion de rotacion (deskew)
            6. Binarizacion adaptativa

        Args:
            image: Imagen en formato numpy array (BGR).

        Returns:
            Imagen preprocesada lista para OCR.
        """
        logger.debug("preprocessing_start", shape=image.shape)

        result = self.resize_if_needed(image)
        result = self.to_grayscale(result)
        result = self.enhance_contrast(result)
        result = self.denoise(result)
        result = self.deskew(result)
        result = self.adaptive_threshold(result)

        logger.debug("preprocessing_complete", shape=result.shape)
        return result

    def resize_if_needed(self, image: np.ndarray, max_dim: int | None = None) -> np.ndarray:
        """Redimensiona manteniendo aspect ratio si excede max_dim.

        Args:
            image: Imagen de entrada.
            max_dim: Dimension maxima del lado largo. Si es None, usa config.

        Returns:
            Imagen redimensionada o la original si no excede.
        """
        max_dim = max_dim or self.config.max_dimension
        height, width = image.shape[:2]
        max_current = max(height, width)

        if max_current <= max_dim:
            return image

        scale = max_dim / max_current
        new_width = int(width * scale)
        new_height = int(height * scale)

        logger.debug("resizing_image", original=(width, height), new=(new_width, new_height))
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convierte a escala de grises.

        Args:
            image: Imagen BGR o ya en escala de grises.

        Returns:
            Imagen en escala de grises (1 canal).
        """
        if len(image.shape) == 2:
            return image
        if image.shape[2] == 1:
            return image.squeeze(axis=2)
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def deskew(self, image: np.ndarray) -> np.ndarray:
        """Corrige rotacion del documento.

        Usa Hough Line Transform para detectar lineas y calcular angulo
        predominante de rotacion. Rota la imagen para corregir.

        Args:
            image: Imagen en escala de grises.

        Returns:
            Imagen con rotacion corregida.
        """
        # Detectar bordes
        edges = cv2.Canny(image, 50, 150, apertureSize=3)

        # Detectar lineas con Hough Transform
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=image.shape[1] // 8,
            maxLineGap=10,
        )

        if lines is None or len(lines) == 0:
            return image

        # Calcular angulos de todas las lineas detectadas
        angles: list[float] = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx = x2 - x1
            dy = y2 - y1
            if abs(dx) < 1:
                continue
            angle = np.degrees(np.arctan2(dy, dx))
            # Solo considerar lineas casi horizontales
            if abs(angle) < self.config.deskew_angle_threshold:
                angles.append(angle)

        if not angles:
            return image

        # Angulo mediano para robustez contra outliers
        median_angle = float(np.median(angles))

        if abs(median_angle) < 0.5:
            return image

        logger.debug("deskew_correction", angle=median_angle)

        # Rotar imagen
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

        return rotated

    def denoise(self, image: np.ndarray) -> np.ndarray:
        """Elimina ruido usando cv2.fastNlMeansDenoising.

        Parametros calibrados para documentos medicos.

        Args:
            image: Imagen en escala de grises.

        Returns:
            Imagen con ruido reducido.
        """
        return cv2.fastNlMeansDenoising(
            image,
            h=self.config.denoise_strength,
            templateWindowSize=7,
            searchWindowSize=21,
        )

    def adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """Binarizacion adaptativa con cv2.adaptiveThreshold.

        Usa ADAPTIVE_THRESH_GAUSSIAN_C para manejar variaciones
        de iluminacion en documentos escaneados.

        Args:
            image: Imagen en escala de grises.

        Returns:
            Imagen binaria (solo valores 0 y 255).
        """
        return cv2.adaptiveThreshold(
            image,
            maxValue=255,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv2.THRESH_BINARY,
            blockSize=self.config.adaptive_block_size,
            C=self.config.adaptive_c,
        )

    def detect_text_regions(
        self, image: np.ndarray
    ) -> list[tuple[int, int, int, int]]:
        """Detecta regiones de texto usando contornos.

        Aplica operaciones morfologicas para conectar caracteres
        en bloques de texto, luego detecta contornos.

        Args:
            image: Imagen en escala de grises o binaria.

        Returns:
            Lista de bounding boxes (x, y, w, h) de regiones con texto.
        """
        # Asegurar imagen binaria invertida (texto blanco, fondo negro)
        if len(np.unique(image)) > 2:
            binary = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
            )
        else:
            binary = cv2.bitwise_not(image) if np.mean(image) > 127 else image

        # Operaciones morfologicas para conectar texto
        kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))

        dilated_h = cv2.dilate(binary, kernel_horizontal, iterations=1)
        dilated = cv2.dilate(dilated_h, kernel_vertical, iterations=1)

        # Encontrar contornos
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrar contornos muy pequenos (ruido)
        min_area = (image.shape[0] * image.shape[1]) * 0.001
        regions: list[tuple[int, int, int, int]] = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area >= min_area and w > 20 and h > 10:
                regions.append((x, y, w, h))

        # Ordenar de arriba a abajo, izquierda a derecha
        regions.sort(key=lambda r: (r[1], r[0]))

        logger.debug("text_regions_detected", count=len(regions))
        return regions

    def correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """Corrige perspectiva si la foto fue tomada en angulo.

        Detecta los 4 corners del documento usando deteccion de contornos
        y aplica warpPerspective para obtener vista frontal.

        Args:
            image: Imagen BGR o escala de grises.

        Returns:
            Imagen con perspectiva corregida, o la original si no se
            detecta un contorno cuadrilateral claro.
        """
        # Trabajar en escala de grises para deteccion
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 75, 200)

        # Dilatar para cerrar gaps en bordes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return image

        # Buscar el contorno mas grande con 4 vertices
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        doc_contour = None
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(approx) == 4:
                # Verificar que el area sea al menos 25% de la imagen
                area = cv2.contourArea(approx)
                image_area = image.shape[0] * image.shape[1]
                if area > image_area * 0.25:
                    doc_contour = approx
                    break

        if doc_contour is None:
            return image

        # Ordenar puntos: top-left, top-right, bottom-right, bottom-left
        points = doc_contour.reshape(4, 2).astype(np.float32)
        ordered = self._order_points(points)

        # Calcular dimensiones del documento destino
        width_top = np.linalg.norm(ordered[1] - ordered[0])
        width_bottom = np.linalg.norm(ordered[2] - ordered[3])
        max_width = int(max(width_top, width_bottom))

        height_left = np.linalg.norm(ordered[3] - ordered[0])
        height_right = np.linalg.norm(ordered[2] - ordered[1])
        max_height = int(max(height_left, height_right))

        dst = np.array(
            [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
            dtype=np.float32,
        )

        matrix = cv2.getPerspectiveTransform(ordered, dst)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))

        logger.debug("perspective_corrected", output_size=(max_width, max_height))
        return warped

    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Mejora contraste con CLAHE.

        Contrast Limited Adaptive Histogram Equalization mejora el
        contraste local sin amplificar ruido excesivamente.

        Args:
            image: Imagen en escala de grises.

        Returns:
            Imagen con contraste mejorado.
        """
        clahe = cv2.createCLAHE(
            clipLimit=self.config.clahe_clip_limit,
            tileGridSize=self.config.clahe_grid_size,
        )
        return clahe.apply(image)

    @staticmethod
    def _order_points(points: np.ndarray) -> np.ndarray:
        """Ordena 4 puntos como: top-left, top-right, bottom-right, bottom-left.

        Args:
            points: Array de 4 puntos (x, y).

        Returns:
            Array de puntos ordenados.
        """
        ordered = np.zeros((4, 2), dtype=np.float32)

        s = points.sum(axis=1)
        ordered[0] = points[np.argmin(s)]   # top-left: menor x+y
        ordered[2] = points[np.argmax(s)]   # bottom-right: mayor x+y

        d = np.diff(points, axis=1)
        ordered[1] = points[np.argmin(d)]   # top-right: menor y-x
        ordered[3] = points[np.argmax(d)]   # bottom-left: mayor y-x

        return ordered
