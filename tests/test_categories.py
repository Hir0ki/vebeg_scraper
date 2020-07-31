from tests.test_parsers import test_proxy
from vebeg_scraper.parser import CategoryParser
import pytest


def test_categories(test_proxy):
    # given
    category_parser = CategoryParser(test_proxy)
    # when
    categories = category_parser.get_categories()
    # then
    assert categories[1].id == 1757
    assert categories[1].name == "Jahreswagen / Kfz. bis 24 Monate"
    assert categories[1].is_top_level is False


def test_categories_has_no_dublicates(test_proxy):
    # given
    category_parser = CategoryParser(test_proxy)
    # when
    categories = category_parser.get_categories()
    list_of_cat_ids = []
    for cat in categories:
        assert cat.id not in list_of_cat_ids
        list_of_cat_ids.append(cat.id)
