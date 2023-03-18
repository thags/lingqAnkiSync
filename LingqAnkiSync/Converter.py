from .Models.Lingq import Lingq
from .Models.AnkiCard import AnkiCard

def ConvertAnkiCardsToLingqs(ankiCards: list[AnkiCard], statusToInterval: dict[int:int]) -> list[Lingq]:
    lingqs = []
    for card in ankiCards:
        lingqs.append(
            Lingq(
                card.primaryKey,
                card.front,
                card.back,
                _ConvertAnkiIntervalToLingqStatus(card.interval, statusToInterval)
        ))
    return lingqs

def ConvertLingqsToAnkiCards(lingqs: list[Lingq], statusToInterval: dict[int:int]) -> list[AnkiCard]:
    ankiCards = []
    for lingq in lingqs:
        ankiCards.append(
            AnkiCard(
                lingq.primaryKey,
                lingq.word,
                lingq.translation,
                _ConvertLingqStatusToAnkiInterval(lingq.status, statusToInterval)
        ))
    return ankiCards

def _ConvertLingqStatusToAnkiInterval(linqStatus: int, statusToInterval: dict[int, int]) -> str:
    return str(statusToInterval[linqStatus])

def _ConvertAnkiIntervalToLingqStatus(interval: int, statusToInterval: dict[int, int]) -> int:
    interval = int(interval)
    return next(
        (key for key, value in statusToInterval.items() if interval <= value),
        4,
    )