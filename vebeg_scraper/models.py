from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum
from pathlib import Path

GEBOTSBASIS_NAMES = ["Stück", "Posten"]


@dataclass
class Category:
    id: int
    name: str
    is_top_level: bool
    parent_id: Optional[int]

    def __init__(
        self, id: int, name: str, parent_id: Optional[int] = None, is_top_level=False
    ):
        if not is_top_level:
            parent_id = None
        self.parent_id = parent_id
        self.id = id
        self.name = name
        self.is_top_level = is_top_level


@dataclass
class Listing:
    id: int
    title: str
    daten: Dict
    kurzbeschreibung: str
    gebotsbasis: str
    lagerort: str
    pictures_paths: List[Path]
    attachments: List[Path]
    category: Category
    gebotstermin: datetime

    @staticmethod
    def parse_gebotstermin(termin: str) -> datetime:
        only_date = termin[14:]
        gebotstermin = datetime.strptime(only_date, "%d.%m.%Y, %H:%M h")
        return gebotstermin


@dataclass
class AuctionResult:
    id: int
    value: int
