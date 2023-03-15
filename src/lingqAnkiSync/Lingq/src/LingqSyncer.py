from . import LingqApi
from .LingqModel import Lingq

class LingqSyncer:
    def __init__(self, apiKey, languageCode):
        self.apiKey = apiKey
        self.languageCode = languageCode
        
    def SyncLingq(self, lingq):
        convertedToLingq = Lingq(
            lingq["primaryKey"], 
            lingq["word"], 
            lingq["translation"], 
            lingq["status"], 
            lingq["extendedStatus"])
        LingqApi.updateLingqStatus(convertedToLingq)

    def ShouldUpdateLingqStatus(self, primarykey, newStatus) -> bool:
        lingqCurrentStatus = LingqApi.getLingqStatus(
            primarykey, self.apiKey, self.languageCode)
        return int(lingqCurrentStatus) < int(newStatus)
    
    def SyncLingqs(self, lingqs) -> int:
        numberOfLingqsUpdated = 0
        for lingq in lingqs:
            if (self.ShouldUpdateLingqStatus(lingq.primaryKey, lingq.status) == True):
                self.SyncLingq(lingq)
                numberOfLingqsUpdated += 1
        return numberOfLingqsUpdated
