from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class Category:
    id: int
    name: str
    is_top_level: bool
    parent_id: int

    def __init__(self, id: int, name: str, parent_id: int=0, is_top_level=False):
        if not is_top_level:
            parent_id = 0
        self.parent_id = parent_id
        self.id = id
        self.name = name


@dataclass
class Listing: 
    id: int
    title: str
    daten: Dict
    kurzbeschreibung: str
    bemerkungen: str
    gebotsbasis: str
    hinweise_bedingungen: str
    lagerort: str
    category: Category
    gebotstermin: datetime

    @staticmethod
    def parse_gebotstermin(termin: str ) -> datetime:
        only_date = termin[14:]
        gebotstermin = datetime.strptime(only_date, "%d.%m.%Y, %H:%M h")
        return gebotstermin