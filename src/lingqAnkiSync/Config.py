import string
from aqt import mw

class Config:
    def __init__(self, config=None):
        self.config = (
            mw.addonManager.getConfig(__name__) if (config is None) else config
        )
    
    def getConfig(self, fieldName: string) -> str:
        value = self.config[fieldName]
        return "" if value is None or value == "" else str(value)

    def setConfig(self, fieldName: string, setTo: string):
        self.config[fieldName] = setTo
        mw.addonManager.writeConfig(__name__, self.config)

    def getApiKey(self):
        return self.getConfig('apiKey')

    def setApiKey(self, setTo: string):
        self.setConfig('apiKey', setTo)

    def getLanguageCode(self):
        return self.getConfig('languageCode')

    def setLanguageCode(self, setTo: string):
        self.setConfig('languageCode', setTo)
        
    def getStatusToInterval(self):
        return self.getConfig('statusToInterval')
