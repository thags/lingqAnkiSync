from Models.Lingq import Lingq

class Config:
    def __init__(self, addonManager):
        self.addonManager = addonManager
        self.config = self.addonManager.getConfig(__name__)

    def _GetConfig(self, fieldName: str) -> str:
        value = self.config[fieldName]
        return "" if value is None or value == "" else str(value)
    
    def _SetConfig(self, fieldName: str, setTo: str):
        self.config[fieldName] = setTo
        self.addonManager.writeConfig(__name__, self.config)

    def GetApiKey(self):
        return self._GetConfig('apiKey')

    def SetApiKey(self, setTo: str):
        self._SetConfig('apiKey', setTo)

    def GetLanguageCode(self):
        return self._GetConfig('languageCode')
    
    def SetLanguageCode(self, setTo: str):
        self._SetConfig('languageCode', setTo)
    
    def GetStatusToInterval(self):
        # Using a default anki ease factor of 2.5, this should make it so
        # that you need to complete two reviews of a card before it updates in
        # lingq with a higher known status
        #
        # e.g. card pulled from linq with status of 'recognized' (5 day review interval).
        # we see it and review it once correctly. card will still sync to lingq
        # as a status of 'recognized' until we see that card again in 32.5 days and review
        # correctly a second time.
        #
        # but also if we hit "easy" just once in anki then that will be sufficient
        # to increase the status to the next level
        return {
            Lingq.LEVEL_1: 0,
            Lingq.LEVEL_2: 5,
            Lingq.LEVEL_3: 13,
            Lingq.LEVEL_4: 34,
            Lingq.LEVEL_KNOWN: 85
        }