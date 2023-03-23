import sys, os
sys.path.append(os.path.realpath(f"./{os.path.dirname(__file__)}"))

import random
from Models.Lingq import Lingq
from Models.AnkiCard import AnkiCard

def ConvertAnkiCardsToLingqs(ankiCards: list[AnkiCard], statusToInterval: dict[int:int]) -> list[Lingq]:
    lingqs = []
    for card in ankiCards:
        lingqs.append(
            Lingq(
                card.primaryKey,
                card.word,
                card.translation,
                _ConvertAnkiIntervalToLingqStatus(card.interval, statusToInterval),
                None
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
                _ConvertLingqStatusToAnkiInterval(lingq.status, lingq.extended_status, statusToInterval)
        ))
    return ankiCards

def _ConvertLingqStatusToAnkiInterval(status: int, extended_status: int, statusToInterval: dict[int, int]) -> int:
    startRange = 0
    endRange = 0
    if (extended_status == 3 and status == 3):
        startRange = statusToInterval[status]
        endRange = sum(statusToInterval.values())
    elif (status >= 0 and status <= 3):
        startRange = statusToInterval[status]
        endRange = statusToInterval[status + 1]
        
    return random.randint(startRange, endRange)


def _ConvertAnkiIntervalToLingqStatus(interval: int, statusToInterval: dict[int, int]) -> int:
    for lingqStatus, ankiInterval in statusToInterval.items():
        if interval <= ankiInterval:
            return lingqStatus
    return max(statusToInterval.keys())
