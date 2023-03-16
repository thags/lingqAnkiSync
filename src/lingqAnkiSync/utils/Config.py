from aqt import mw

class Config:
    def __init__(self, config=None):
        self.config = (
            mw.addonManager.getConfig(__name__) if (config is None) else config
        )
    
    def GetConfig(self, fieldName: str) -> str:
        value = self.config[fieldName]
        return "" if value is None or value == "" else str(value)
    
    def SetConfig(self, fieldName: str, setTo: str):
        self.config[fieldName] = setTo
        mw.addonManager.writeConfig(__name__, self.config)

    def GetApiKey(self):
        return self.GetConfig('apiKey')

    def SetApiKey(self, setTo: str):
        self.SetConfig('apiKey', setTo)

    def GetLanguageCode(self):
        return self.GetConfig('languageCode')
    
    def SetLanguageCode(self, setTo: str):
        self.SetConfig('languageCode', setTo)
    
    def GetStatusToInterval(self):
        return self.GetConfig('statusToInterval')