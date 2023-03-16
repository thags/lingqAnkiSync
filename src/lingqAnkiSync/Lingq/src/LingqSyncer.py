class LingqSyncer:
    def __init__(self, LingqApi):
        self.lingqApi = LingqApi
    
    def ShouldUpdateLingqStatus(self, primarykey, newStatus) -> bool:
        lingqCurrentStatus = self.lingqApi.getLingqStatus(primarykey)
        return int(lingqCurrentStatus) < int(newStatus)
    
    def SyncLingqs(self, lingqs) -> int:
        numberOfLingqsUpdated = 0
        for lingq in lingqs:
            if (self.ShouldUpdateLingqStatus(lingq["PrimaryKey"], lingq["Interval"]) == True):
                self.lingqApi.updateLingqStatus(lingq)
                numberOfLingqsUpdated += 1
        return numberOfLingqsUpdated