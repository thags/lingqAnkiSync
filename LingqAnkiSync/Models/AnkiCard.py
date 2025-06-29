from dataclasses import dataclass
from typing import List


@dataclass
class AnkiCard:
    primaryKey: int
    word: str
    translations: List[str]
    interval: int
    status: str
    tags: List[str]
    sentence: str
    importance: int
    popularity: int = 0
