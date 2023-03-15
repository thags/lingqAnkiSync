#statusToInterval = {0: 0, 1: 5, 2: 10, 3: 20, 4: 40}
from ..Lingq.src.LingqModel import Lingq

class Helpers:
    def __init__(self, statusToInverval=None):
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

    def convertLinqStatusToAnkiDueDate(self, linqStatus: int) -> str:
        return self.statusToInverval[linqStatus]
    
    def ConvertAnkiCardToLingq(self, ankiCard) -> Lingq:
        return Lingq(
            ankiCard['note']['fields']['LingqPrimaryKey'], 
            ankiCard['note']['fields']['Word'], 
            ankiCard['note']['fields']['Translation'], 
            self.convertAnkiIntervalToLingqStatus(ankiCard['due']))
        
    def ConvertAnkiCardsToLingqs(self, ankiCards) -> list:
        return [self.ConvertAnkiCardToLingq(ankiCard) for ankiCard in ankiCards]
