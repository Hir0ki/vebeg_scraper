from vebeg_scraper.models import Listing, Category
from datetime import datetime


def test_parse_gebotstermin_20_07_2020():
    #given
    datum_string = "Gebotstermin: 20.07.2020, 13:00 h"
    #when
    result = Listing.parse_gebotstermin(datum_string)
    #then
    assert datetime(2020,7,20,13,0) == result

def test_parse_gebotstermin_01_07_2020():
    #given
    datum_string = "Gebotstermin: 01.07.2020, 13:00 h"
    #when
    result = Listing.parse_gebotstermin(datum_string)
    #then
    assert datetime(2020,7,1,13,0) == result
def test_category_init_is_top_level():
    #given
    given_parent_id = 10
    given_is_top_level = True
    #when
    test = Category(1,"a", given_parent_id, is_top_level=given_is_top_level )
    #then
    assert test.parent_id == 10

def test_category_init_is_top_level():
    #given
    given_parent_id = 10
    given_is_top_level = False
    #when
    test = Category(1,"a", given_parent_id, is_top_level=given_is_top_level )
    #then
    assert test.parent_id == 0