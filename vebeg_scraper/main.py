import logging
import prometheus_client
import schedule
import time
from vebeg_scraper import settings
from vebeg_scraper.parser import CategoryParser, ListingsParser, AuctionResultsParser
from vebeg_scraper.serializer.json_serializer import JsonSerializer
from vebeg_scraper.serializer.postgres_serializer.postgress_serializer import Database
from vebeg_scraper.proxy import RequestProxy
from vebeg_scraper import settings


if settings.DEBUG_MODE is True:
    import debugpy

    debugpy.listen(5678)

s = RequestProxy("https://www.vebeg.de")
prometheus_client.start_http_server(settings.PROMEHTEUS_PORT)
output = JsonSerializer(settings.JSON_SERIALIZER_OUTPUT_PATH)
database = Database(
    host=settings.PG_HOST,
    username=settings.PG_USER,
    password=settings.PG_PASS,
    database=settings.PG_DB,
)


def run_scraper():
    cat = CategoryParser(s)
    cats = cat.get_categories()
    output.serializer_categories(cats)
    database.write_categories(cats)

    results = AuctionResultsParser(s).get_all_results()
    output.serializer_auction_results(results)
    [database.update_listing_with_price(result) for result in results]

    listing = ListingsParser(s, cats, database, settings.VEBEG_DOWNLOAD_PICUTRES)
    listings = listing.get_listings()
    output.serializer_listings(listings)


logging.info("Starting scrping")
time.sleep(10)
run_scraper()
logging.info("Done scraping")
schedule.every(2).days.do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(1)
