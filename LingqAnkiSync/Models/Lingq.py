from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Lingq:
    LEVEL_1 = "new"
    LEVEL_2 = "recognized"
    LEVEL_3 = "familiar"
    LEVEL_4 = "learned"
    LEVEL_KNOWN = "known"
    LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_KNOWN]

    primaryKey: int
    word: str
    translations: List[str]
    status: int
    extendedStatus: int
    tags: List[str]
    fragment: str
    importance: int
    popularity: int = 0  # Loose proxy for word frequency

    @staticmethod
    def GetPrevLevel(level: str) -> Optional[str]:
        if level == Lingq.LEVEL_1:
            return None

        return Lingq.LEVELS[Lingq.LEVELS.index(level) - 1]

    @staticmethod
    def GetNextLevel(level: str) -> Optional[str]:
        if level == Lingq.LEVEL_KNOWN:
            return None

        return Lingq.LEVELS[Lingq.LEVELS.index(level) + 1]
