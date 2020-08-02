import logging
from vebeg_scraper import settings
from vebeg_scraper.parser import CategoryParser, ListingsParser
from vebeg_scraper.serializer.json_serializer import JsonSerializer
from vebeg_scraper.proxy import RequestProxy

s = RequestProxy("https://www.vebeg.de")

output = JsonSerializer(settings.JSON_SERIALIZER_OUTPUT_PATH)

cat = CategoryParser(s)
cats = cat.get_categories()
output.serializer_categories(cats)

listing = ListingsParser(s, cats)
listings = listing.get_listings()
output.serializer_listings(listings)
