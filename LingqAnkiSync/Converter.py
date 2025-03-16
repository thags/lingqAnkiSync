import random
from typing import List, Dict
import sys

import os
sys.path.append(os.path.realpath(f"{os.path.dirname(__file__)}"))
from Models.Lingq import Lingq
from Models.AnkiCard import AnkiCard

def ConvertAnkiCardsToLingqs(ankiCards: List[AnkiCard], statusToInterval: Dict[int,int]) -> List[Lingq]:
    lingqs = []
    for card in ankiCards:
        lingqs.append(
            Lingq(
                card.primaryKey,
                card.word,
                card.translations,
                _ConvertAnkiIntervalToLingqStatus(card.interval, statusToInterval),
                card.extended_status,
                card.tags,
                card.sentence,
                card.importance,
                card.status
        ))
    return lingqs

def ConvertLingqsToAnkiCards(lingqs: List[Lingq], statusToInterval: Dict[int,int]) -> List[AnkiCard]:
    ankiCards = []
    for lingq in lingqs:
        ankiCards.append(
            AnkiCard(
                lingq.primaryKey,
                lingq.word,
                lingq.translations,
                _ConvertLingqStatusToAnkiInterval(lingq.status, lingq.extended_status, statusToInterval),
                lingq.status,
                lingq.extended_status,
                lingq.tags,
                lingq.fragment,
                lingq.importance
        ))
    return ankiCards

def _ConvertLingqStatusToAnkiInterval(status: int, extended_status: int, statusToInterval: Dict[int,int]) -> int:
    startRange = 0
    endRange = 0
    if (extended_status == 3 and status == 3):
        startRange = statusToInterval[status]
        endRange = statusToInterval[status + 1]
    elif (status > 0 and status <= 3):
        startRange = statusToInterval[status -1]
        endRange = statusToInterval[status]
    elif (status == 0):
        startRange = 0
        endRange = statusToInterval[status]
    else:
        return 0
    return random.randint(startRange, endRange)


def _ConvertAnkiIntervalToLingqStatus(interval: int, statusToInterval: Dict[int,int]) -> int:
    if (interval is None or interval <= 0):
        return 0
    for lingqStatus, ankiInterval in statusToInterval.items():
        if interval <= ankiInterval:
            return lingqStatus
    return max(statusToInterval.keys())