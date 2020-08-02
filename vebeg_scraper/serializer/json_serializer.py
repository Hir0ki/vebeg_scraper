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

    def serializer_categoriy(self, categories: List[Category]):
       json_cateogires = json.dumps([ cat.__dict__ for cat in  categories ])
       self.output_path.joinpath("categories.json").write_text(json_cateogires)
    
    def serializer_listings(self, listings: List[Listing]):
        for entry in listings:
            entry.category = entry.category.__dict__ 
        json_listings = json.dumps([ listing.__dict__ for listing in listings ])
        self.output_path.joinpath("listings.json").write_text(json_listings)