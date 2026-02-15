"""
Manejo de imagenes para el pipeline OCR.

Carga imagenes desde archivos, bytes o arrays numpy,
validando formatos y aplicando conversiones necesarias.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp"}
MAX_FILE_SIZE_MB = 10


class ImageHandler:
    """Manejo de carga y validacion de imagenes para OCR.

    Soporta multiples formatos de imagen y convierte todo
    a arrays numpy BGR para el pipeline OpenCV.
    """

    def load_from_path(self, path: str | Path) -> np.ndarray:
        """Carga una imagen desde ruta de archivo.

        Args:
            path: Ruta al archivo de imagen.

        Returns:
            Imagen como numpy array BGR.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el formato no es soportado o el archivo es muy grande.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")

        if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise ValueError(
                f"Formato no soportado: {path.suffix}. "
                f"Formatos validos: {SUPPORTED_IMAGE_EXTENSIONS}"
            )

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(
                f"Archivo excede el limite de {MAX_FILE_SIZE_MB}MB: {file_size_mb:.1f}MB"
            )

        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"No se pudo leer la imagen: {path}")

        logger.debug("image_loaded", path=str(path), shape=image.shape, size_mb=f"{file_size_mb:.1f}")
        return image

    def load_from_bytes(self, data: bytes) -> np.ndarray:
        """Carga una imagen desde bytes en memoria.

        Args:
            data: Bytes de la imagen.

        Returns:
            Imagen como numpy array BGR.

        Raises:
            ValueError: Si los bytes no representan una imagen valida.
        """
        if len(data) == 0:
            raise ValueError("Datos de imagen vacios")

        file_size_mb = len(data) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(
                f"Imagen excede el limite de {MAX_FILE_SIZE_MB}MB: {file_size_mb:.1f}MB"
            )

        np_arr = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("No se pudo decodificar la imagen desde bytes")

        logger.debug("image_loaded_from_bytes", shape=image.shape)
        return image

    def load_from_pil(self, pil_image: Image.Image) -> np.ndarray:
        """Convierte imagen PIL a numpy array BGR.

        Args:
            pil_image: Imagen PIL.

        Returns:
            Imagen como numpy array BGR.
        """
        if pil_image.mode == "RGBA":
            pil_image = pil_image.convert("RGB")
        elif pil_image.mode == "L":
            return np.array(pil_image)
        elif pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        rgb_array = np.array(pil_image)
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

    @staticmethod
    def is_supported(filename: str) -> bool:
        """Verifica si el archivo tiene extension de imagen soportada.

        Args:
            filename: Nombre del archivo.

        Returns:
            True si el formato es soportado.
        """
        return Path(filename).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
