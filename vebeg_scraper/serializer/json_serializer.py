from vebeg_scraper.models import Category, Listing
from typing import List
from datetime import datetime
import json
import pathlib


class JsonSerializer:
    def __init__(self, output_path: str):
        self.output_path = pathlib.Path(output_path)
        if not self.output_path.is_dir():
            self.output_path.mkdir()

    def serializer_categories(self, categories: List[Category]) -> pathlib.Path:
        json_cateogires = json.dumps([cat.__dict__ for cat in categories])
        cat_output_path = self.output_path.joinpath("categories.json")
        cat_output_path.write_text(json_cateogires)
        return cat_output_path

    def serializer_listings(self, listings: List[Listing]) -> pathlib.Path:
        new_listings = []
        for entry in listings:
            entry.category = entry.category.__dict__  # type: ignore
            entry.gebotstermin = str(entry.gebotstermin)  # type: ignore
            new_listings.append(entry)
        json_listings = json.dumps([listing.__dict__ for listing in new_listings])
        listings_output_path = self.output_path.joinpath("listings.json")
        listings_output_path.write_text(json_listings)
        return listings_output_path