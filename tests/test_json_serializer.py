from vebeg_scraper.models import Listing, Category
from vebeg_scraper.serializer.json_serializer import JsonSerializer
from json import loads
from datetime import datetime
import pytest
import json


@pytest.fixture
def get_test_data():
    categories = [
        Category(id=1270, name="fdas", is_top_level=False, parent_id=1120),
        Category(id=1000, name="Farzeuge", is_top_level=True),
    ]
    listings = [
        Listing(
            id=2032160001,
            title="dfasfdsa",
            daten={},
            kurzbeschreibung="fdas",
            gebotsbasis="fdaf",
            lagerort="fdassd",
            attachments=[],
            pictures_paths=[],
            category=categories[0],
            gebotstermin=datetime(2020, 4, 23, 13, 0),
        ),
        Listing(
            id=2032170001,
            title="dfasfdsa",
            daten={},
            kurzbeschreibung="fdas",
            gebotsbasis="fdaf",
            lagerort="fdassd",
            attachments=[],
            pictures_paths=[],
            category=categories[1],
            gebotstermin=datetime(2020, 4, 23, 13, 0),
        ),
    ]
    return (categories, listings)


def test_categories_serilizer(get_test_data, tmpdir):
    # given
    output_path = tmpdir
    categories = get_test_data[0]
    serializer = JsonSerializer(output_path)
    # when
    cat_path = serializer.serializer_categories(categories)
    # then
    results = json.loads(cat_path.read_text())
    assert results[0].get("id") == 1270
    assert results[1].get("id") == 1000


def test_listings_serilizer(get_test_data, tmpdir):
    output_path = tmpdir
    listings = get_test_data[1]
    serializer = JsonSerializer(output_path)
    # when
    listings_path = serializer.serializer_listings(listings)
    # then
    results = json.loads(listings_path.read_text())
    assert results[0].get("id") == 2032160001
    assert results[1].get("id") == 2032170001
