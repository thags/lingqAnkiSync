from .src.LingqImporter import LingqImporter
from .src.LingqSyncer import LingqSyncer

class LingqController:
    def __init__(self, apiKey, languageCode):
        self.apiKey = apiKey
        self.languageCode = languageCode
    
    def GetFormattedLingqs(self):
        lingqImporter = LingqImporter(self.apiKey, self.languageCode)
        UnformattedLingqs = lingqImporter.GetLingqs()
        return lingqImporter.FormatLingqs(UnformattedLingqs)
    
    def SyncLingqs(self, lingqs):
        self.LingqSyncer = LingqSyncer(self.apiKey, self.languageCode)
        return self.LingqSyncer.SyncLingqs(lingqs)