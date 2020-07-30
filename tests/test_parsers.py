from vebeg_scraper.parser import CategoryParser, ListingsParser
from vebeg_scraper.models import Category
from tests.proxy_test import TestProxy
from datetime import datetime
import pytest  # type: ignore


@pytest.fixture
def test_proxy():
    return TestProxy("")


def test_categories(test_proxy):
    # given
    category_parser = CategoryParser(test_proxy)
    # when
    categories = category_parser.get_categories()
    # then
    assert categories[0].id == 1000
    assert categories[0].is_top_level == True


# def test_get_all_listings(test_proxy):
#    categories = [Category(id=1000,name="",is_top_level=True)]
#    listing_parse = ListingsParser(test_proxy, categories)
#    listings = listing_parse.get_listings()
#    assert listings != []


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
    assert listing.title == "Pkw BMW 740eiPerformance"


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


# def test_prase_listing_gebotsbasis(test_proxy):
#    categories = [Category(id=1100,name="",is_top_level=False)]
#    parser = ListingsParser(test_proxy, categories)
#    listing = parser._parse_lisitng("test_listing", categories[0])
#    assert "stück" ==  listing.gebotsbasis
