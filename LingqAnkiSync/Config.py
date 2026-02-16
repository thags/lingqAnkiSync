from .Models.Lingq import Lingq
from typing import Dict

# fmt: off
lingqLangcodes = [
    'ar','hk','ca','zh','cs','da','nl','fi','el','he','id','it','ja','ko','la','no','fa','pl','pt',
    'ro','ru','sv','tr','uk','af','hy','be','bg','eo','ka','gu','hi','hu','is','km','mk','ms','pa',
    'sk','sl','sw','tl','vi', 'en', 'fr', 'de', 'es'
]
# fmt: on


class Config:
    def __init__(self, addonManager):
        self.addonManager = addonManager
        self.config = self.addonManager.getConfig(__name__)

    def _GetConfig(self, fieldName: str) -> str:
        value = self.config[fieldName]
        return "" if value is None or value == "" else str(value)

    def _SetConfig(self, fieldName: str, set_to: str):
        self.config[fieldName] = set_to
        self.addonManager.writeConfig(__name__, self.config)

    def GetApiKey(self):
        return self._GetConfig("apiKey")

    def SetApiKey(self, set_to: str):
        self._SetConfig("apiKey", set_to)

    def GetLanguageCode(self):
        return self._GetConfig("languageCode")

    def SetLanguageCode(self, set_to: str):
        self._SetConfig("languageCode", set_to)

    def GetLastDeck(self):
        return self._GetConfig("lastDeck")

    def SetLastDeck(self, set_to: str):
        self._SetConfig("lastDeck", set_to)

    def GetLastImportKnowns(self):
        value = self.config.get("lastImportKnowns", False)
        return bool(value)

    def SetLastImportKnowns(self, set_to: bool):
        self._SetConfig("lastImportKnowns", set_to)

    def GetLastDowngradeLingqs(self):
        value = self.config.get("lastDowngradeLingqs", False)
        return bool(value)

    def SetLastDowngradeLingqs(self, set_to: bool):
        self._SetConfig("lastDowngradeLingqs", set_to)

    def GetLevelToInterval(self) -> Dict[str, int]:
        # Using a default anki ease factor of 2.5, this should make it so
        # that you need to complete two reviews of a card before it updates in
        # lingq with a higher known level
        #
        # e.g. card pulled from linq with level of 'recognized' (5 day review interval).
        # we see it and review it once correctly. card will still sync to lingq
        # as a level of 'recognized' until we see that card again in 32.5 days and review
        # correctly a second time.
        #
        # but also if we hit "easy" just once in anki then that will be sufficient
        # to increase the level to the next level (except for new cards)
        return {
            Lingq.LEVEL_1: 0,
            Lingq.LEVEL_2: 5,
            Lingq.LEVEL_3: 13,
            Lingq.LEVEL_4: 34,
            Lingq.LEVEL_KNOWN: 85,
        }