"""
Tests unitarios para MedicalReferenceScraper.

Verifica el parsing de HTML para extraer medicamentos
y codigos CIE-10.
"""

import json
from pathlib import Path

import pytest

from app.utils.scraper import MedicalReferenceScraper, ScrapedCIE10Code, ScrapedMedication


@pytest.fixture
def scraper(tmp_path: Path) -> MedicalReferenceScraper:
    """Crea un scraper con cache en directorio temporal."""
    return MedicalReferenceScraper(cache_dir=str(tmp_path))


@pytest.fixture
def medications_html() -> str:
    """HTML con tabla de medicamentos."""
    return """
    <html>
    <body>
        <table>
            <tr><th>Medicamento</th><th>Presentacion</th><th>Indicaciones</th></tr>
            <tr><td>Metformina</td><td>Tabletas 850mg</td><td>Diabetes tipo 2</td></tr>
            <tr><td>Losartan</td><td>Tabletas 50mg</td><td>Hipertension</td></tr>
            <tr><td>Omeprazol</td><td>Capsulas 20mg</td><td>Gastritis</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def cie10_html() -> str:
    """HTML con tabla de codigos CIE-10."""
    return """
    <html>
    <body>
        <table>
            <tr><th>Codigo</th><th>Descripcion</th><th>Categoria</th></tr>
            <tr><td>E11.9</td><td>Diabetes mellitus tipo 2 sin complicaciones</td><td>Endocrinas</td></tr>
            <tr><td>I10</td><td>Hipertension esencial</td><td>Circulatorias</td></tr>
            <tr><td>K29.7</td><td>Gastritis no especificada</td><td>Digestivas</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def list_html() -> str:
    """HTML con lista de medicamentos (sin tabla)."""
    return """
    <html>
    <body>
        <ul>
            <li>Metformina 850mg</li>
            <li>Losartan 50mg</li>
            <li>Aspirina 100mg</li>
        </ul>
    </body>
    </html>
    """


class TestScrapeMedicationsFromHtml:
    """Tests para scraping de medicamentos."""

    def test_extracts_medications_from_table(
        self, scraper: MedicalReferenceScraper, medications_html: str
    ) -> None:
        """Extrae medicamentos de tabla HTML."""
        meds = scraper.scrape_medications_from_html(medications_html)
        assert len(meds) == 3
        assert all(isinstance(m, ScrapedMedication) for m in meds)

    def test_medication_fields(
        self, scraper: MedicalReferenceScraper, medications_html: str
    ) -> None:
        """Los medicamentos tienen campos correctos."""
        meds = scraper.scrape_medications_from_html(medications_html)
        first = meds[0]
        assert first.generic_name == "Metformina"
        assert first.presentation == "Tabletas 850mg"
        assert first.indications == "Diabetes tipo 2"

    def test_fallback_to_list(
        self, scraper: MedicalReferenceScraper, list_html: str
    ) -> None:
        """Si no hay tabla, extrae de lista."""
        meds = scraper.scrape_medications_from_html(list_html)
        assert len(meds) == 3

    def test_empty_html(self, scraper: MedicalReferenceScraper) -> None:
        """HTML vacio retorna lista vacia."""
        meds = scraper.scrape_medications_from_html("<html><body></body></html>")
        assert meds == []


class TestScrapeCIE10FromHtml:
    """Tests para scraping de codigos CIE-10."""

    def test_extracts_codes_from_table(
        self, scraper: MedicalReferenceScraper, cie10_html: str
    ) -> None:
        """Extrae codigos CIE-10 de tabla HTML."""
        codes = scraper.scrape_cie10_from_html(cie10_html)
        assert len(codes) == 3
        assert all(isinstance(c, ScrapedCIE10Code) for c in codes)

    def test_code_fields(
        self, scraper: MedicalReferenceScraper, cie10_html: str
    ) -> None:
        """Los codigos tienen campos correctos."""
        codes = scraper.scrape_cie10_from_html(cie10_html)
        first = codes[0]
        assert first.code == "E11.9"
        assert "Diabetes" in first.name
        assert first.category == "Endocrinas"

    def test_empty_html(self, scraper: MedicalReferenceScraper) -> None:
        """HTML vacio retorna lista vacia."""
        codes = scraper.scrape_cie10_from_html("<html><body></body></html>")
        assert codes == []


class TestSaveToJson:
    """Tests para guardado de datos scrapeados."""

    def test_saves_medications(
        self, scraper: MedicalReferenceScraper, medications_html: str
    ) -> None:
        """Guarda medicamentos a JSON."""
        meds = scraper.scrape_medications_from_html(medications_html)
        path = scraper.save_to_json(meds, "test_meds.json")
        assert path.exists()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3
        assert data[0]["generic_name"] == "Metformina"

    def test_saves_cie10(
        self, scraper: MedicalReferenceScraper, cie10_html: str
    ) -> None:
        """Guarda codigos CIE-10 a JSON."""
        codes = scraper.scrape_cie10_from_html(cie10_html)
        path = scraper.save_to_json(codes, "test_cie10.json")
        assert path.exists()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3

    def test_creates_directory(self, tmp_path: Path) -> None:
        """Crea directorio si no existe."""
        cache_dir = tmp_path / "new_dir" / "sub"
        scraper = MedicalReferenceScraper(cache_dir=str(cache_dir))
        assert cache_dir.exists()
