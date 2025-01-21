import random
from typing import List, Dict, Tuple
import sys

import os
sys.path.append(os.path.realpath(f"./{os.path.dirname(__file__)}"))
from Models.Lingq import Lingq
from Models.AnkiCard import AnkiCard

def AnkiCardsToLingqs(anki_cards: List[AnkiCard], status_to_interval: Dict[str,int]) -> List[Lingq]:
    lingqs = []
    for card in anki_cards:
        lingqs.append(
            Lingq(
                card.primaryKey,
                card.word,
                card.translations,
                *_LingqStatusToInternalStatus(_AnkiIntervalToLingqStatus(card.interval, status_to_interval)),
                card.tags,
                card.sentence,
                card.importance,
                card.status
        ))
    return lingqs

def LingqsToAnkiCards(lingqs: List[Lingq], statusToInterval: Dict[str,int]) -> List[AnkiCard]:
    ankiCards = []
    for lingq in lingqs:
        ankiCards.append(
            AnkiCard(
                primarykey=lingq.primaryKey,
                word=lingq.word,
                translations=lingq.translations,
                interval=_LingqStatusToAnkiInterval(lingq.status, lingq.extended_status, statusToInterval),
                status=_LingqInternalStatusToStatus(lingq.status, lingq.extended_status),
                tags=lingq.tags,
                sentence=lingq.fragment,
                importance=lingq.importance,
                popularity=lingq.popularity
        ))
    return ankiCards

def CardCanIncreaseStatus(anki_card: AnkiCard, statusToInterval: Dict[str,int]):
    return anki_card.interval > statusToInterval[anki_card.status]

def _LingqStatusToAnkiInterval(status: int, extended_status: int, status_to_interval: Dict[str,int]) -> int:
    known_status = _LingqInternalStatusToStatus(status, extended_status)
    interval_range = (0, 0)

    if known_status == 'new':
        interval_range = (0, status_to_interval[known_status])
    elif known_status == 'recognized':
        interval_range = (status_to_interval[known_status], status_to_interval['familiar'])
    elif known_status == 'familiar':
        interval_range = (status_to_interval[known_status], status_to_interval['learned'])
    elif known_status == 'learned':
        interval_range = (status_to_interval[known_status], status_to_interval['known'])
    elif known_status == 'known':
        # If a card is known, how long should the range be? Double?
        interval_range = (status_to_interval[known_status], status_to_interval[known_status] * 2)

    r = random.randint(interval_range[0], interval_range[1])
    return r

def _AnkiIntervalToLingqStatus(interval: int, status_to_interval: Dict[str,int]) -> str:
    if interval > status_to_interval['known']:
        known_status = 'known'
    else:
        known_status = max([
            k for k,v in status_to_interval.items() if interval > v
        ], default='new')

    return known_status

def _LingqInternalStatusToStatus(internal_status: int, extended_status: int) -> str:
    if internal_status not in (0, 1, 2, 3) or extended_status not in (None, 0, 3):
        raise ValueError(
            f'''Lingq api status outside of accepted range
            Status: {internal_status}
            Extended Status: {extended_status}
        ''')

    if extended_status == 3:
        known_status = Lingq.LEVELS[4]
    else:
        known_status = Lingq.LEVELS[internal_status]

    return known_status

def _LingqStatusToInternalStatus(status: str) -> Tuple[int, int]:
    if status not in Lingq.LEVELS:
        raise ValueError(f'No such status "{status}". Should be one of {Lingq.LEVELS}')

    extended_status = 0
    if status == 'known':
        internal_status = 3
        extended_status = 3
    else:
        internal_status = Lingq.LEVELS.index(status)

    return internal_status, extended_status
