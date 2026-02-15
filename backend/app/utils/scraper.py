"""
Scraper de referencia medica usando BeautifulSoup.

Obtiene datos de referencia de fuentes publicas como el cuadro
basico de medicamentos y el catalogo CIE-10 en espanol.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScrapedMedication:
    """Medicamento scrapeado."""

    generic_name: str
    commercial_name: Optional[str] = None
    presentation: Optional[str] = None
    indications: Optional[str] = None
    contraindications: Optional[str] = None
    source_url: Optional[str] = None


@dataclass
class ScrapedCIE10Code:
    """Codigo CIE-10 scrapeado."""

    code: str
    name: str
    category: Optional[str] = None
    chapter: Optional[str] = None


class MedicalReferenceScraper:
    """Scraper de referencias medicas mexicanas.

    Obtiene datos de fuentes publicas para enriquecer el catalogo
    de referencia del sistema.
    """

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; DocSaludMX/1.0; "
            "+https://github.com/docsalud-mx)"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "es-MX,es;q=0.9",
    }

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        """Inicializa el scraper.

        Args:
            cache_dir: Directorio para cachear resultados. Default: data/reference.
        """
        self.cache_dir = Path(cache_dir) if cache_dir else (
            Path(__file__).resolve().parent.parent.parent / "data" / "reference"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def scrape_medications_from_html(self, html_content: str) -> list[ScrapedMedication]:
        """Parsea medicamentos de contenido HTML.

        Busca tablas o listas con informacion de medicamentos
        y extrae nombre generico, presentacion e indicaciones.

        Args:
            html_content: HTML crudo de la pagina.

        Returns:
            Lista de ScrapedMedication.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        medications: list[ScrapedMedication] = []

        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    generic_name = cells[0].get_text(strip=True)
                    presentation = cells[1].get_text(strip=True) if len(cells) > 1 else None
                    indications = cells[2].get_text(strip=True) if len(cells) > 2 else None

                    if generic_name and len(generic_name) > 2:
                        medications.append(ScrapedMedication(
                            generic_name=generic_name,
                            presentation=presentation,
                            indications=indications,
                        ))

        if not medications:
            lists = soup.find_all(["ul", "ol"])
            for lst in lists:
                items = lst.find_all("li")
                for item in items:
                    text = item.get_text(strip=True)
                    if text and len(text) > 3:
                        medications.append(ScrapedMedication(generic_name=text))

        return medications

    def scrape_cie10_from_html(self, html_content: str) -> list[ScrapedCIE10Code]:
        """Parsea codigos CIE-10 de contenido HTML.

        Args:
            html_content: HTML crudo de la pagina.

        Returns:
            Lista de ScrapedCIE10Code.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        codes: list[ScrapedCIE10Code] = []

        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    code = cells[0].get_text(strip=True)
                    name = cells[1].get_text(strip=True)
                    category = cells[2].get_text(strip=True) if len(cells) > 2 else None

                    if code and name:
                        codes.append(ScrapedCIE10Code(
                            code=code,
                            name=name,
                            category=category,
                        ))

        return codes

    def fetch_with_retry(
        self,
        url: str,
        max_retries: int = 3,
        backoff_base: float = 1.0,
    ) -> Optional[str]:
        """Fetch URL con retry y backoff exponencial.

        Args:
            url: URL a consultar.
            max_retries: Numero maximo de reintentos.
            backoff_base: Base del backoff exponencial en segundos.

        Returns:
            Contenido HTML como string, o None si falla.
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or "utf-8"
                return response.text
            except requests.RequestException as e:
                wait_time = backoff_base * (2 ** attempt)
                logger.warning(
                    "scraper_fetch_retry",
                    url=url,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                    wait_seconds=wait_time,
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)

        logger.error("scraper_fetch_failed", url=url, max_retries=max_retries)
        return None

    def save_to_json(self, data: list[Any], filename: str) -> Path:
        """Guarda datos scrapeados a JSON.

        Args:
            data: Lista de dataclasses o dicts a guardar.
            filename: Nombre del archivo (sin directorio).

        Returns:
            Path al archivo guardado.
        """
        output_path = self.cache_dir / filename
        serializable = []
        for item in data:
            if hasattr(item, "__dataclass_fields__"):
                from dataclasses import asdict
                serializable.append(asdict(item))
            else:
                serializable.append(item)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)

        logger.info("scraper_data_saved", path=str(output_path), count=len(data))
        return output_path
