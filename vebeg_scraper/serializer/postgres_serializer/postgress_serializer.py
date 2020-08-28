import psycopg2
import time
import pathlib
import logging
import json
from typing import List
from typing import List
from vebeg_scraper import settings
from vebeg_scraper.models import Category, Listing, AuctionResult


class Database:
    def __init__(self, host: str, username: str, password: str, database: str):
        count = 0
        self.logger = logging.getLogger("scraper.database")
        self.logger.info("connection to db")
        while count < 10:
            try:
                self.connection = psycopg2.connect(
                    host=host, database=database, user=username, password=password
                )
                break
            except psycopg2.OperationalError as er:
                self.logger.warning(
                    f"couldn't't connect to db after {count} tries", exc_info=er
                )
                time.sleep(1)
                count + 1
            self.logger.error("couldn't connect to db after 10 seconds")
        if count > 10:
            raise psycopg2.OperationalError()

    def write_categories(self, categories: List[Category]):
        self.logger.debug(f"write {len(categories)} to database")
        cusor = self.connection.cursor()
        existing_cat_id = [cat.id for cat in self.read_all_cateogires()]
        cats_to_write = [cat for cat in categories if cat.id not in existing_cat_id]
        for cat in cats_to_write:
            self.logger.debug(f"insert category: {cat.id} into db")
            cusor.execute(
                "INSERT INTO Categories (id, name, is_top_level, parent_id) VALUES(%s,%s,%s,%s)",
                (cat.id, cat.name, cat.is_top_level, cat.parent_id),
            )
        self.connection.commit()
        cusor.close()

    def read_all_cateogires(self) -> List[Category]:
        self.logger.debug("reading categories from database")
        cur = self.connection.cursor()
        cur.execute("SELECT id, name, is_top_level, parent_id FROM Categories")
        return [
            Category(id=cat[0], name=cat[1], is_top_level=cat[2], parent_id=cat[3])
            for cat in cur.fetchall()
        ]

    def write_listing(self, listing: Listing):
        cur = self.connection.cursor()
        self.logger.debug(f"Writeing listing: {listing}")
        try:
            cur.execute(
                """INSERT INTO Listings ( id, title, data, kurzbeschreibung, gebotsbasis, lagerort, gebotstermin, category_id ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    listing.id,
                    listing.title,
                    json.dumps(listing.daten),
                    listing.kurzbeschreibung,
                    listing.gebotsbasis,
                    listing.lagerort,
                    listing.gebotstermin,
                    listing.category.id,
                ),
            )
        except psycopg2.Error:
            self.logger.warning(f"duplicate listing with id: {listing.id}")

        self.connection.commit()
        cur.close()

    def update_listing_with_price(self, result: AuctionResult):
        cur = self.connection.cursor()
        self.logger.debug(f"Update listing: {result.id} with price {result.value}")
        try:
            cur.execute(
                "UPDATE Listings SET sold_price = %s WHERE id = %s;",
                (result.id, result.value),
            )
        except psycopg2.Error as err:
            self.logger.warning(
                f"Listing {result.id} couldn't update price with error {err.__name__} "
            )
            self.connection.rollback()
        self.connection.commit()
        cur.close()
