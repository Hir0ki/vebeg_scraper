from vebeg_scraper.models import Listing
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