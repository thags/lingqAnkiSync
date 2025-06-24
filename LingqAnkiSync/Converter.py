import random
from typing import List, Dict, Tuple
from .Models.Lingq import Lingq
from .Models.AnkiCard import AnkiCard


def AnkiCardsToLingqs(
    ankiCards: List[AnkiCard], statusToInterval: Dict[str, int]
) -> List[Lingq]:
    lingqs = []
    for card in ankiCards:
        status, extendedStatus = LingqStatusToInternalStatus(
            _AnkiIntervalToLingqStatus(card.interval, statusToInterval)
        )
        lingqs.append(
            Lingq(
                primaryKey=card.primaryKey,
                word=card.word,
                translations=card.translations,
                status=status,
                extendedStatus=extendedStatus,
                tags=card.tags,
                fragment=card.sentence,
                importance=card.importance,
                popularity=card.popularity,
            )
        )
    return lingqs


def LingqsToAnkiCards(lingqs: List[Lingq], statusToInterval: Dict[str, int]) -> List[AnkiCard]:
    ankiCards = []
    for lingq in lingqs:
        ankiCards.append(
            AnkiCard(
                primaryKey=lingq.primaryKey,
                word=lingq.word,
                translations=lingq.translations,
                interval=_LingqStatusToAnkiInterval(
                    lingq.status, lingq.extendedStatus, statusToInterval
                ),
                status=LingqInternalStatusToStatus(lingq.status, lingq.extendedStatus),
                tags=lingq.tags,
                sentence=lingq.fragment,
                importance=lingq.importance,
                popularity=lingq.popularity,
            )
        )
    return ankiCards


def CardCanIncreaseStatus(ankiCard: AnkiCard, statusToInterval: Dict[str, int]):
    return ankiCard.interval > statusToInterval[ankiCard.status]


def _LingqStatusToAnkiInterval(
    status: int, extendedStatus: int, statusToInterval: Dict[str, int]
) -> int:
    knownStatus = LingqInternalStatusToStatus(status, extendedStatus)
    intervalRange = (0, 0)

    if knownStatus == Lingq.LEVEL_1:
        intervalRange = (0, statusToInterval[knownStatus])
    elif knownStatus == Lingq.LEVEL_2:
        intervalRange = (statusToInterval[knownStatus], statusToInterval[Lingq.LEVEL_3])
    elif knownStatus == Lingq.LEVEL_3:
        intervalRange = (statusToInterval[knownStatus], statusToInterval[Lingq.LEVEL_4])
    elif knownStatus == Lingq.LEVEL_4:
        intervalRange = (statusToInterval[knownStatus], statusToInterval[Lingq.LEVEL_KNOWN])
    elif knownStatus == Lingq.LEVEL_KNOWN:
        # If a card is known, how long should the range be? Double?
        intervalRange = (statusToInterval[knownStatus], statusToInterval[knownStatus] * 2)

    r = random.randint(intervalRange[0], intervalRange[1])
    return r


def _AnkiIntervalToLingqStatus(interval: int, statusToInterval: Dict[str, int]) -> str:
    if interval > statusToInterval[Lingq.LEVEL_KNOWN]:
        knownStatus = Lingq.LEVEL_KNOWN
    else:
        knownStatus = Lingq.LEVEL_1
        for level in Lingq.LEVELS:
            if interval > statusToInterval[level]:
                knownStatus = level

    return knownStatus


def LingqInternalStatusToStatus(internalStatus: int, extendedStatus: int) -> str:
    if internalStatus not in (0, 1, 2, 3) or extendedStatus not in (None, 1, 0, 3):
        raise ValueError(
            f"""Lingq api status outside of accepted range
            Status: {internalStatus}
            Extended Status: {extendedStatus}
        """
        )

    if extendedStatus == 3:
        knownStatus = Lingq.LEVELS[4]
    else:
        knownStatus = Lingq.LEVELS[internalStatus]

    return knownStatus


def LingqStatusToInternalStatus(status: str) -> Tuple[int, int]:
    if status not in Lingq.LEVELS:
        raise ValueError(f'No such status "{status}". Should be one of {Lingq.LEVELS}')

    extendedStatus = 0
    if status == "known":
        internalStatus = 3
        extendedStatus = 3
    else:
        internalStatus = Lingq.LEVELS.index(status)

    return internalStatus, extendedStatus
