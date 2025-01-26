import random
from typing import List, Dict, Tuple
import sys

import os

sys.path.append(os.path.realpath(f"./{os.path.dirname(__file__)}"))
from Models.Lingq import Lingq
from Models.AnkiCard import AnkiCard


def anki_cards_to_lingqs(
    anki_cards: List[AnkiCard], status_to_interval: Dict[str, int]
) -> List[Lingq]:
    lingqs = []
    for card in anki_cards:
        lingqs.append(
            Lingq(
                card.primary_key,
                card.word,
                card.translations,
                *lingq_status_to_internal_status(
                    _anki_interval_to_lingq_status(card.interval, status_to_interval)
                ),
                card.tags,
                card.sentence,
                card.importance,
                card.status,
            )
        )
    return lingqs


def lingqs_to_anki_cards(lingqs: List[Lingq], status_to_interval: Dict[str, int]) -> List[AnkiCard]:
    anki_cards = []
    for lingq in lingqs:
        anki_cards.append(
            AnkiCard(
                primary_key=lingq.primary_key,
                word=lingq.word,
                translations=lingq.translations,
                interval=_lingq_status_to_anki_interval(
                    lingq.status, lingq.extended_status, status_to_interval
                ),
                status=lingq_internal_status_to_status(lingq.status, lingq.extended_status),
                tags=lingq.tags,
                sentence=lingq.fragment,
                importance=lingq.importance,
                popularity=lingq.popularity,
            )
        )
    return anki_cards


def card_can_increase_status(anki_card: AnkiCard, status_to_interval: Dict[str, int]):
    return anki_card.interval > status_to_interval[anki_card.status]


def _lingq_status_to_anki_interval(
    status: int, extended_status: int, status_to_interval: Dict[str, int]
) -> int:
    known_status = lingq_internal_status_to_status(status, extended_status)
    interval_range = (0, 0)

    if known_status == Lingq.LEVEL_1:
        interval_range = (0, status_to_interval[known_status])
    elif known_status == Lingq.LEVEL_2:
        interval_range = (status_to_interval[known_status], status_to_interval[Lingq.LEVEL_3])
    elif known_status == Lingq.LEVEL_3:
        interval_range = (status_to_interval[known_status], status_to_interval[Lingq.LEVEL_4])
    elif known_status == Lingq.LEVEL_4:
        interval_range = (status_to_interval[known_status], status_to_interval[Lingq.LEVEL_KNOWN])
    elif known_status == Lingq.LEVEL_KNOWN:
        # If a card is known, how long should the range be? Double?
        interval_range = (status_to_interval[known_status], status_to_interval[known_status] * 2)

    r = random.randint(interval_range[0], interval_range[1])
    return r


def _anki_interval_to_lingq_status(interval: int, status_to_interval: Dict[str, int]) -> str:
    if interval > status_to_interval[Lingq.LEVEL_KNOWN]:
        known_status = Lingq.LEVEL_KNOWN
    else:
        known_status = Lingq.LEVEL_1
        for level in Lingq.LEVELS:
            if interval > status_to_interval[level]:
                known_status = level

    return known_status


def lingq_internal_status_to_status(internal_status: int, extended_status: int) -> str:
    if internal_status not in (0, 1, 2, 3) or extended_status not in (None, 0, 3):
        raise ValueError(
            f"""Lingq api status outside of accepted range
            Status: {internal_status}
            Extended Status: {extended_status}
        """
        )

    if extended_status == 3:
        known_status = Lingq.LEVELS[4]
    else:
        known_status = Lingq.LEVELS[internal_status]

    return known_status


def lingq_status_to_internal_status(status: str) -> Tuple[int, int]:
    if status not in Lingq.LEVELS:
        raise ValueError(f'No such status "{status}". Should be one of {Lingq.LEVELS}')

    extended_status = 0
    if status == "known":
        internal_status = 3
        extended_status = 3
    else:
        internal_status = Lingq.LEVELS.index(status)

    return internal_status, extended_status
