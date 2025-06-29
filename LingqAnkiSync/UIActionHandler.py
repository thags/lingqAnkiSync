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
        statusToInterval = self.config.GetStatusToInterval()

        self._CheckLanguageCode(languageCode)

        lingqs = LingqApi(apiKey, languageCode).GetLingqs(importKnowns)
        cards = LingqsToAnkiCards(lingqs, statusToInterval)
        return AnkiHandler.CreateNotesFromCards(cards, deckName, self.config.GetLanguageCode())

    def SyncLingqStatusToLingq(
        self, deckName: str, downgrade: bool = False, progressCallback=None
    ) -> Tuple[int, int, int]:
        apiKey = self.config.GetApiKey()
        languageCode = self.config.GetLanguageCode()
        statusToInterval = self.config.GetStatusToInterval()

        self._CheckLanguageCode(languageCode)

        cards = AnkiHandler.GetAllCardsInDeck(deckName)
        cardsToIncrease, cardsToDecrease = self._PrepCardsForUpdate(
            cards, statusToInterval, downgrade
        )
        cardsToUpdate = cardsToIncrease + cardsToDecrease

        lingqs = AnkiCardsToLingqs(cardsToUpdate, statusToInterval)
        successfulUpdates = LingqApi(apiKey, languageCode).SyncStatusesToLingq(
            lingqs, progressCallback
        )
        self._UpdateNotesInAnki(deckName, cardsToUpdate)

        return len(cardsToIncrease), len(cardsToDecrease), successfulUpdates

    def _CheckLanguageCode(self, languageCode: str):
        if languageCode and languageCode not in lingqLangcodes:
            raise ValueError(
                f'Language code "{languageCode}" is not valid. Examples include "es", "de", "ja", etc.'
            )

    def _PrepCardsForUpdate(
        self, ankiCards: List[AnkiCard], statusToInterval: Dict[str, int], downgrade: bool
    ) -> Tuple[List[AnkiCard], List[AnkiCard]]:
        """pre-checking if cards should update, to limit API calls later on
        and prepping card for update in anki db

        :returns two lists of cards that need to be updated in LingQ
        """
        cardsToIncrease = []
        cardsToDecrease = []

        for card in ankiCards:
            nextLevel = Lingq.GetNextLevel(card.status)
            prevLevel = Lingq.GetPrevLevel(card.status)
            if nextLevel is not None and (card.interval > statusToInterval[nextLevel]):
                card.status = nextLevel
                cardsToIncrease.append(card)

            if (
                downgrade
                and prevLevel is not None
                and card.interval < statusToInterval[card.status]
            ):
                card.status = prevLevel
                cardsToDecrease.append(card)

        return cardsToIncrease, cardsToDecrease

    def _UpdateNotesInAnki(self, deckName: str, cards: List[AnkiCard]):
        for card in cards:
            AnkiHandler.UpdateCardStatus(deckName, card.primaryKey, card.status)

    def SetConfigs(self, apiKey, languageCode):
        self.config.SetApiKey(apiKey)
        self.config.SetLanguageCode(languageCode)

    def GetDeckNames(self) -> List:
        return AnkiHandler.GetAllDeckNames()

    def GetApiKey(self) -> str:
        return self.config.GetApiKey()

    def GetLanguageCode(self) -> str:
        return self.config.GetLanguageCode()
