#statusToInterval = {0: 0, 1: 5, 2: 10, 3: 20, 4: 40}
from ..Lingq.src.LingqModel import Lingq
from datetime import datetime

class Helpers:
    def __init__(self, statusToInverval={0: 0, 1: 5, 2: 10, 3: 20, 4: 40}):
        if statusToInverval is None:
            from .Config import Config
            self.config = Config()
            self.statusToInverval = self.config.getStatusToInterval()
        else:
            self.statusToInverval = statusToInverval
    
    def convertAnkiIntervalToLingqStatus(self, interval) -> int:
        interval = int(interval)
        return next(
            (key for key, value in self.statusToInverval.items() if interval <= value),
            4,
        )

    def convertLinqStatusToAnkiInterval(self, linqStatus: int) -> str:
        return self.statusToInverval[linqStatus]
    
    def ConvertAnkiCardToLingq(self, ankiCard) -> Lingq:
        return Lingq(
            ankiCard.note()["LingqPK"],
            ankiCard.note()["Front"],
            ankiCard.note()["Back"],
            self.convertAnkiIntervalToLingqStatus(ankiCard.ivl))
        
    def ConvertAnkiCardsToLingqs(self, ankiCards) -> list:
        return [self.ConvertAnkiCardToLingq(ankiCard) for ankiCard in ankiCards]
    
    def ConvertLingqsToAnkiCards(self, lingqs) -> list:
        return [self.ConvertLingqToAnkiCard(lingq) for lingq in lingqs]
    
    def ConvertLingqToAnkiCard(self, lingq) -> dict:
        return {
            "PrimaryKey": lingq.primaryKey,
            "Word": lingq.word,
            "Translation": lingq.translation,
            "Status": lingq.status,
            "Interval": self.convertLinqStatusToAnkiInterval(lingq.status)
        }
