from .src.LingqImporter import LingqImporter
from .src.LingqSyncer import LingqSyncer
from ....LingqAnkiSync.LingqApi import LingqAPI
from ....LingqAnkiSync.Models.Lingq import Lingq

class LingqController:
    def __init__(self, apiKey, languageCode):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self.lingqAPi = LingqAPI(apiKey, languageCode)
    
    def GetLingqs(self) -> list[Lingq]:
        lingqImporter = LingqImporter(self.lingqAPi)
        return lingqImporter.GetFormattedLingqs()
    
    def SyncLingqs(self, lingqs: list[Lingq]) -> int:
        lingqSyncer = LingqSyncer(self.lingqAPi)
        return lingqSyncer.SyncLingqs(lingqs)