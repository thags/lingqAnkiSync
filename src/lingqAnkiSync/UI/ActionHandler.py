from ..Lingq.LingqController import LingqController
from ..utils.Config import Config
from ..Anki import AnkiHandler

class ActionHandler:
    def __init__(self, addonManager):
        self.config = Config(addonManager)

    def ImportLingqsToAnki(self, deckName) -> int:
        apiKey = self.GetApiKey()
        languageCode = self.GetLanguageCode()
        lingqController = LingqController(apiKey, languageCode)
        lingqs = lingqController.GetLingqs()
        return AnkiHandler.CreateNotesFromLingqs(lingqs, deckName)
    
    def SyncLingqStatusToLingq(self, deckName) -> int:
        apiKey = self.config.GetApiKey()
        languageCode = self.config.GetLanguageCode()
        lingqController = LingqController(apiKey, languageCode)
        lingqsInDeck = AnkiHandler.GetAllLingqsInDeck(deckName)
        return lingqController.SyncLingqs(lingqsInDeck)

    def SetConfigs(self, apiKey, languageCode):
        self.config.SetApiKey(apiKey)
        self.config.SetLanguageCode(languageCode)
    
    def GetDeckNames(self) -> list:
        return AnkiHandler.GetAllDeckNames()
    
    def GetApiKey(self) -> str:
        return self.config.GetApiKey()
    
    def GetLanguageCode(self) -> str:
        return self.config.GetLanguageCode()