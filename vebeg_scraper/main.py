import logging
import prometheus_client
import schedule
import time
from vebeg_scraper import settings
from vebeg_scraper.parser import CategoryParser, ListingsParser, AuctionResultsParser
from vebeg_scraper.serializer.json_serializer import JsonSerializer
from vebeg_scraper.proxy import RequestProxy
from vebeg_scraper import settings

s = RequestProxy("https://www.vebeg.de")
prometheus_client.start_http_server(settings.PROMEHTEUS_PORT)
output = JsonSerializer(settings.JSON_SERIALIZER_OUTPUT_PATH)


def run_scraper():
    cat = CategoryParser(s)
    cats = cat.get_categories()
    output.serializer_categories(cats)

    resutls = AuctionResultsParser(s).get_all_results()
    output.serializer_auction_results(resutls)

    listing = ListingsParser(s, cats)
    listings = listing.get_listings()
    output.serializer_listings(listings)


logging.info("Starting scrping")
time.sleep(5000)
run_scraper()

schedule.every(2).days.do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(1)
