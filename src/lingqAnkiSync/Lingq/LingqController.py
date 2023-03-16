from .src.LingqImporter import LingqImporter
from .src.LingqSyncer import LingqSyncer
from .src.LingqApi import LingqAPI

class LingqController:
    def __init__(self, apiKey, languageCode):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self.lingqAPi = LingqAPI(apiKey, languageCode)
    
    def GetFormattedLingqs(self):
        lingqImporter = LingqImporter(self.lingqAPi)
        UnformattedLingqs = lingqImporter.GetLingqs()
        return lingqImporter.FormatLingqs(UnformattedLingqs)
    
    def SyncLingqs(self, lingqs):
        lingqSyncer = LingqSyncer(self.lingqAPi)
        return lingqSyncer.SyncLingqs(lingqs)