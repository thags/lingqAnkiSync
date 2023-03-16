from .LingqApi import LingqAPI
from .LingqModel import Lingq

class LingqSyncer:
    def __init__(self, apiKey, languageCode):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self.lingqApi = LingqAPI(apiKey, languageCode)

    def ShouldUpdateLingqStatus(self, primarykey, newStatus) -> bool:
        lingqCurrentStatus = self.lingqApi.getLingqStatus(primarykey)
        return int(lingqCurrentStatus) < int(newStatus)
    
    def SyncLingqs(self, lingqs) -> int:
        numberOfLingqsUpdated = 0
        for lingq in lingqs:
            if (self.ShouldUpdateLingqStatus(lingq.primaryKey, lingq.status) == True):
                self.lingqApi.updateLingqStatus(lingq)
                numberOfLingqsUpdated += 1
        return numberOfLingqsUpdated
