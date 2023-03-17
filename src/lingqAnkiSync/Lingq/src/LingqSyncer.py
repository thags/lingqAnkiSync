from ...Models.Lingq import Lingq
class LingqSyncer:
    def __init__(self, LingqApi):
        self.lingqApi = LingqApi
    
    def ShouldUpdateLingqStatus(self, primarykey, newStatus) -> bool:
        lingqCurrentStatus = self.lingqApi.getLingqStatus(primarykey)
        return int(lingqCurrentStatus) < int(newStatus)
    
    def SyncLingqs(self, lingqs: list[Lingq]) -> int:
        numberOfLingqsUpdated = 0
        for lingq in lingqs:
            if (self.ShouldUpdateLingqStatus(lingq.primaryKey, lingq.status) == True):
                self.lingqApi.updateLingqStatus(lingq)
                numberOfLingqsUpdated += 1
        return numberOfLingqsUpdated