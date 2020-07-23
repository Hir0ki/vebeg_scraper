import logging
from vebeg_scraper.parser import CategoryParser, ListingsParser
from vebeg_scraper.proxy import RequestProxy

s = RequestProxy("https://www.vebeg.de")

cat = CategoryParser(s)
cats = cat.get_categories()

l = ListingsParser(s, cats)
print(len(l.get_listings()))