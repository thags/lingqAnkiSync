from ..Lingq.LingqController import LingqController
from ..utils.Config import Config
from ..Anki import AnkiHandler
from ..utils.Helpers import Helpers

class ActionHandler:
    def __init__(self):
        self.config = Config()
        self.helpers = Helpers()

    def ImportLingqsToAnki(self, deckName) -> int:
        apiKey = self.GetApiKey()
        languageCode = self.GetLanguageCode()
        lingqController = LingqController(apiKey, languageCode)
        lingqs = lingqController.GetFormattedLingqs()
        return AnkiHandler.CreateNotesWithInterval(lingqs, deckName)
    
    def SyncLingqStatusToLingq(self, deckName) -> int:
        apiKey = self.config.GetApiKey()
        languageCode = self.config.GetLanguageCode()
        lingqController = LingqController(apiKey, languageCode)
        lingqsInDeck = AnkiHandler.GetAllObjectsInDeck(deckName)
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