"""
Tipos y dataclasses para el modulo OCR.

Define las estructuras de datos para resultados de OCR,
bloques de texto con posicion, y configuracion del pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TextBlock:
    """Bloque de texto extraido con informacion de posicion.

    Args:
        text: Contenido textual del bloque.
        confidence: Confianza del OCR (0-100).
        bbox: Bounding box como tupla (x, y, w, h).
        page: Numero de pagina (0-indexed).
        block_type: Tipo de bloque ('paragraph', 'header', 'table_cell').
    """

    text: str
    confidence: float
    bbox: tuple[int, int, int, int]
    page: int = 0
    block_type: str = "paragraph"


@dataclass
class OCRResult:
    """Resultado completo de una extraccion OCR.

    Args:
        text: Texto completo extraido.
        confidence: Confianza promedio (0-100).
        page_count: Numero de paginas procesadas.
        blocks: Lista de bloques de texto con posicion.
        processing_time_ms: Tiempo de procesamiento en milisegundos.
        warnings: Lista de advertencias generadas durante el procesamiento.
    """

    text: str
    confidence: float
    page_count: int
    blocks: list[TextBlock] = field(default_factory=list)
    processing_time_ms: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass
class PreprocessConfig:
    """Configuracion para el pipeline de preprocesamiento.

    Args:
        max_dimension: Dimension maxima del lado largo en pixeles.
        denoise_strength: Fuerza del denoising (h parameter de fastNlMeans).
        adaptive_block_size: Tamano de bloque para binarizacion adaptativa.
        adaptive_c: Constante C para binarizacion adaptativa.
        clahe_clip_limit: Clip limit para CLAHE.
        clahe_grid_size: Grid size para CLAHE.
        deskew_angle_threshold: Angulo maximo de correccion en grados.
    """

    max_dimension: int = 3000
    denoise_strength: int = 10
    adaptive_block_size: int = 11
    adaptive_c: int = 2
    clahe_clip_limit: float = 2.0
    clahe_grid_size: tuple[int, int] = (8, 8)
    deskew_angle_threshold: float = 15.0
