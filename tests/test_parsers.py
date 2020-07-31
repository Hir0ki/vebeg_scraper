from vebeg_scraper.parser import CategoryParser, ListingsParser, clean_string
from vebeg_scraper.models import Category
from tests.proxy_test import TestProxy
from datetime import datetime
import pytest  # type: ignore
import pathlib


@pytest.fixture
def test_proxy():
    return TestProxy("")


def test_clean_string():
    assert (
        clean_string("Jahreswagen\n\t\t\t\t\t\t\t\t\t\t\t\t/ Kfz. bis 24 Monate")
        == "Jahreswagen / Kfz. bis 24 Monate"
    )


def test_get_all_listings(test_proxy):
    categories = [
        Category(id=1000, name="", is_top_level=True),
        Category(id=1757, name="", is_top_level=False),
    ]
    listing_parse = ListingsParser(test_proxy, categories)
    listings = listing_parse.get_listings()
    assert listings != []


def test_parse_listing_id(test_proxy):
    # given
    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    listing = parser._parse_lisitng("test_listing", categories[0])
    assert listing.id == 2030520001


def test_prase_listing_title(test_proxy):
    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    listing = parser._parse_lisitng("test_listing", categories[0])
    assert listing.title == "Pkw BMW 740e iPerformance"


def test_parse_listing_gebotstermin(test_proxy):
    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    listing = parser._parse_lisitng("test_listing", categories[0])
    assert listing.gebotstermin == datetime(2020, 7, 24, 13, 0)


def test_parse_listing_kurzbeschreibung(test_proxy):
    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    listing = parser._parse_lisitng("test_listing", categories[0])
    assert (
        "oft-Close-Automatik" in listing.kurzbeschreibung
        and "Frontbereich/-schiebe" in listing.kurzbeschreibung
    )


def test_prase_listing_gebotsbasis(test_proxy):
    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    listing = parser._parse_lisitng("test_listing", categories[0])
    assert "stück" == listing.gebotsbasis.lower()


def test_parse_lagerort(test_proxy):
    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    listing = parser._parse_lisitng("test_listing", categories[0])
    assert "Grellstraße" in listing.lagerort
    assert "10409 Berlin" in listing.lagerort
    assert "Lagerort / Standort" not in listing.lagerort


def test_parse_daten(test_proxy):
    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    listing = parser._parse_lisitng("test_listing", categories[0])
    assert listing.daten.get("Erstzulassung") == "09/18"


def test_download_image(test_proxy, tmpdir):

    categories = [Category(id=1100, name="", is_top_level=False)]
    parser = ListingsParser(test_proxy, categories)
    parser.download_dir = pathlib.Path(tmpdir.dirname)
    parser._parse_lisitng("test_listing", categories[0])
    new_line = parser.download_dir.joinpath("2030520001_0.jpg")
    assert new_line.is_file() is True
