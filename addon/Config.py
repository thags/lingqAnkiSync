import string
from aqt import mw

def getConfig(fieldName: string):
    config = mw.addonManager.getConfig(__name__)
    value = config[fieldName]
    if (value == None or value == ""):
        return str(fieldName)

def setConfig(fieldName: string, setTo: string):
    if (setTo != getConfig(fieldName)):
        config = mw.addonManager.getConfig(__name__)
        config[fieldName] = setTo
        mw.addonManager.writeConfig(__name__, config)

def getApiKey():
    return getConfig('apiKey')

def setApiKey(setTo: string):
    setConfig('apiKey', setTo)
    
def getLanguageCode():
    return getConfig('languageCode')

def setLanguageCode(setTo: string):
    setConfig('languageCode', setTo)