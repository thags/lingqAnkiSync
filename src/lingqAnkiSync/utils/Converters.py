def _AnkiIntervalToLingqStatus(interval, statusToInterval) -> int:
        interval = int(interval)
        return next(
            (key for key, value in statusToInterval.items() if interval <= value),
            4,
        )
        
def _LinqStatusToAnkiInterval(linqStatus: int, statusToInterval) -> str:
    return statusToInterval[linqStatus]

def AnkiCardsToLingqs(ankiCards, statusToInterval):
    lingqs = []
    for card in ankiCards:
        lingqs.append(Lingq(
            card.note()["LingqPK"],
            card.note()["Front"],
            card.note()["Back"],
            card.ivl
        ))
    return lingqs
