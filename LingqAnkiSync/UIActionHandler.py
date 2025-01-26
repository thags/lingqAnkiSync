from .Converter import AnkiCardsToLingqs, LingqsToAnkiCards
from .AnkiHandler import CreateNotesFromCards, GetAllCardsInDeck, GetAllDeckNames
from .LingqApi import LingqApi
from .Config import Config
from .Models.Lingq import Lingq
from typing import List

class ActionHandler:
    def __init__(self, addonManager):
        self.config = Config(addonManager)

    def ImportLingqsToAnki(self, deckName:str, import_knowns: bool) -> int:
        apiKey = self.GetApiKey()
        languageCode = self.GetLanguageCode()
        statusToInterval = self.config.GetStatusToInterval()

        lingqs = LingqApi(apiKey, languageCode, import_knowns).GetLingqs()
        cards = LingqsToAnkiCards(lingqs, statusToInterval)
        return CreateNotesFromCards(cards, deckName)

    def SyncLingqStatusToLingq(self, deckName) -> int:
        apiKey = self.config.GetApiKey()
        languageCode = self.config.GetLanguageCode()
        statusToInterval = self.config.GetStatusToInterval()

        cards = GetAllCardsInDeck(deckName)
        # pre-checking if cards should update, to limit API calls later on
        cards_to_update = self._FindCardsToUpdate(cards, statusToInterval)
        lingqs = AnkiCardsToLingqs(cards_to_update, statusToInterval)

        return LingqApi(apiKey, languageCode).SyncStatusesToLingq(lingqs)

    def _FindCardsToUpdate(self, ankiCards, statusToInterval):
        cards_to_update = []

        for card in ankiCards:
            if(card.status != Lingq.LEVEL_KNOWN):
                next_level = Lingq.LEVELS[Lingq.LEVELS.index(card.status)+1]
                next_level_interval = statusToInterval[next_level]

                if card.interval > next_level_interval:
                    cards_to_update.append(card)

        return cards_to_update

    def SetConfigs(self, apiKey, languageCode):
        self.config.SetApiKey(apiKey)
        self.config.SetLanguageCode(languageCode)

    def GetDeckNames(self) -> List:
        return GetAllDeckNames()

    def GetApiKey(self) -> str:
        return self.config.GetApiKey()

    def GetLanguageCode(self) -> str:
        return self.config.GetLanguageCode()