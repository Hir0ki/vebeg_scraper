from vebeg_scraper.models import Category, Listing, AuctionResult
from typing import List
from datetime import datetime
import json
import pathlib


class JsonSerializer:
    def __init__(self, output_path: str):
        self.output_path = pathlib.Path(output_path)
        self.date: datetime = datetime.now()
        if not self.output_path.is_dir():
            self.output_path.mkdir()

    def serializer_categories(self, categories: List[Category]) -> pathlib.Path:
        json_cateogires = json.dumps([cat.__dict__ for cat in categories])
        cat_output_path = self.output_path.joinpath(
            f"categories_{self.date.year}_{self.date.month}_{self.date.day}_{self.date.hour}.json"
        )
        cat_output_path.write_text(json_cateogires)
        return cat_output_path

    def serializer_listings(self, listings: List[Listing]) -> pathlib.Path:
        new_listings = []
        for entry in listings:
            entry.category = entry.category.__dict__  # type: ignore
            entry.gebotstermin = str(entry.gebotstermin)  # type: ignore
            entry.pictures_paths = [str(path) for path in entry.pictures_paths]  # type: ignore
            new_listings.append(entry)
        json_listings = json.dumps([listing.__dict__ for listing in new_listings])
        listings_output_path = self.output_path.joinpath(
            "listings_{self.date.year}_{self.date.month}_{self.date.day}_{self.date.hour}.json"
        )
        listings_output_path.write_text(json_listings)
        return listings_output_path

    def serializer_auction_results(self, resutls: List[AuctionResult]) -> pathlib.Path:
        new_results = []
        for entry in resutls:
            entry.gebotstermin = str(entry.gebotstermin)  # type: ignore
            new_results.append(entry)
        json_resutls = json.dumps([result.__dict__ for result in new_results])
        output_path = self.output_path.joinpath(
            "resutls_{self.date.year}_{self.date.month}_{self.date.day}_{self.date.hour}.json"
        )
        output_path.write_text(json_resutls)
        return output_path
