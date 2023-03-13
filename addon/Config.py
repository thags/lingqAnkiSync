import string
from aqt import mw


def getConfig(fieldName: string) -> str:
    config = mw.addonManager.getConfig(__name__)
    value = config[fieldName]
    return "" if value is None or value == "" else str(value)


def setConfig(fieldName: string, setTo: string):
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
