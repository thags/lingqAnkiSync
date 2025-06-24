from LingqAnkiSync.Config import Config
import pytest


class ConfigRepo:
    def __init__(self, apiKey, languageCode):
        self.apikey = apiKey
        self.languageCode = languageCode
        self.itemSet = None

    def getConfig(self, name):
        return {"apiKey": self.apikey, "languageCode": self.languageCode}

    def writeConfig(self, name, setTo):
        self.itemSet = setTo


@pytest.fixture
def addonManager():
    return ConfigRepo("testApiKey", "testLanguageCode")


class TestGets:
    def test_should_get_api_key(self, addonManager):
        result = Config(addonManager).GetApiKey()
        assert result == "testApiKey"

    def test_should_get_language_code(self, addonManager):
        result = Config(addonManager).GetLanguageCode()
        assert result == "testLanguageCode"

    def test_should_get_deafult_status_to_interval(self, addonManager):
        result = Config(addonManager).GetStatusToInterval()
        assert result == {"new": 0, "recognized": 5, "familiar": 13, "learned": 34, "known": 85}


class TestSets:
    def test_should_set_api_key(self, addonManager):
        Config(addonManager).SetApiKey("testSetApiKey")
        assert addonManager.itemSet["apiKey"] == "testSetApiKey"

    def test_should_set_language_code(self, addonManager):
        Config(addonManager).SetLanguageCode("testSetLanguageCode")
        assert addonManager.itemSet["languageCode"] == "testSetLanguageCode"
