from .Converter import AnkiCardsToLingqs, LingqsToAnkiCards
from .LingqApi import LingqApi
from .Config import Config, lingqLangcodes
from .Models.Lingq import Lingq
from .Models.AnkiCard import AnkiCard
from typing import List, Dict, Tuple
from . import AnkiHandler


class ActionHandler:
    def __init__(self, addonManager):
        self.config = Config(addonManager)

    def ImportLingqsToAnki(self, deckName: str, importKnowns: bool) -> int:
        apiKey = self.config.GetApiKey()
        languageCode = self.config.GetLanguageCode()
        levelToInterval = self.config.GetLevelToInterval()

        self._CheckLanguageCode(languageCode)

        lingqs = LingqApi(apiKey, languageCode).GetLingqs(importKnowns)
        cards = LingqsToAnkiCards(lingqs, levelToInterval)
        return AnkiHandler.CreateNotesFromCards(cards, deckName, self.config.GetLanguageCode())

    def SyncLingqStatusToLingq(
        self, deckName: str, downgrade: bool = False, progressCallback=None
    ) -> Tuple[int, int, int, int]:
        apiKey = self.config.GetApiKey()
        languageCode = self.config.GetLanguageCode()
        levelToInterval = self.config.GetLevelToInterval()

        self._CheckLanguageCode(languageCode)

        cards = AnkiHandler.GetAllCardsInDeck(deckName)
        cardsToIncrease, cardsToDecrease, cardsToIgnore = self._PrepCardsForUpdate(
            cards, levelToInterval, downgrade
        )
        cardsToUpdate = cardsToIncrease + cardsToDecrease

        lingqs = AnkiCardsToLingqs(cardsToUpdate, levelToInterval)
        successfulUpdates = LingqApi(apiKey, languageCode).SyncStatusesToLingq(
            lingqs, progressCallback
        )
        self._UpdateNotesInAnki(deckName, cardsToUpdate)

        return len(cardsToIncrease), len(cardsToDecrease), len(cardsToIgnore), successfulUpdates

    def _CheckLanguageCode(self, languageCode: str):
        if languageCode not in lingqLangcodes:
            raise ValueError(
                f'Language code "{languageCode}" is not valid. Examples include "es", "de", "ja", etc.'
            )

    def _PrepCardsForUpdate(
        self, ankiCards: List[AnkiCard], levelToInterval: Dict[str, int], downgrade: bool
    ) -> Tuple[List[AnkiCard], List[AnkiCard]]:
        """pre-checking if cards should update, to limit API calls later on
        and prepping card for update in anki db

        :returns three lists of cards that need to be updated in LingQ or ignored due to not being the right noteType
        """
        cardsToIncrease = []
        cardsToDecrease = []
        cardsToIgnore = []

        for card in ankiCards:
            # If the card is not using our schema
            if card.level is None:
                cardsToIgnore.append(card)
            else:
               nextLevel = Lingq.GetNextLevel(card.level)
               prevLevel = Lingq.GetPrevLevel(card.level)
               if nextLevel is not None and (card.interval > levelToInterval[nextLevel]):
                   card.level = nextLevel
                   cardsToIncrease.append(card)

               if (
                   downgrade
                   and prevLevel is not None
                   and card.interval < levelToInterval[card.level]
               ):
                   card.level = prevLevel
                   cardsToDecrease.append(card)

        return cardsToIncrease, cardsToDecrease, cardsToIgnore

    def _UpdateNotesInAnki(self, deckName: str, cards: List[AnkiCard]):
        for card in cards:
            AnkiHandler.UpdateCardLevel(deckName, card.primaryKey, card.level)

    def SetConfigs(self, apiKey, languageCode):
        self.config.SetApiKey(apiKey)
        self.config.SetLanguageCode(languageCode)

    def GetDeckNames(self) -> List:
        return AnkiHandler.GetAllDeckNames()

    def GetApiKey(self) -> str:
        return self.config.GetApiKey()

    def GetLanguageCode(self) -> str:
        return self.config.GetLanguageCode()

    def GetLastDeck(self) -> str:
        return self.config.GetLastDeck()

    def SetLastDeck(self, set_to: str):
        self.config.SetLastDeck(set_to)

    def GetLastImportKnowns(self) -> bool:
        return self.config.GetLastImportKnowns()

    def SetLastImportKnowns(self, set_to: bool):
        self.config.SetLastImportKnowns(set_to)

    def GetLastDowngradeLingqs(self) -> bool:
        return self.config.GetLastDowngradeLingqs()

    def SetLastDowngradeLingqs(self, set_to: bool):
        self.config.SetLastDowngradeLingqs(set_to)
