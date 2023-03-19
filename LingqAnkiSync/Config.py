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
        return {0: 1, 1: 5, 2: 10, 3: 20, 4: 40}