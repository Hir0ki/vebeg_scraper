from vebeg_scraper.parser import CategoryParser, ListingsParser 
from tests.proxy_test import TestProxy
import pytest



@pytest.fixture
def test_proxy():
    return TestProxy("")


def test_categories(test_proxy):
    #given
    category_parser = CategoryParser(test_proxy) 
    #when
    categories = category_parser.get_categories()
    #then
    assert categories[0].id == 1000 
    assert categories[0].is_top_level == True

def test_listing(test_proxy):
    categories = 
    listing_parse = ListingsParser(test_proxy)
