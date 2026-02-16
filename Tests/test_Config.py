from LingqAnkiSync.Config import Config
import pytest


class ConfigRepo:
    def __init__(self, apiKey, languageCode, lastDeck="", lastImportKnowns=False, lastDowngradeLingqs=False):
        self.apikey = apiKey
        self.languageCode = languageCode
        self.lastDeck = lastDeck
        self.lastImportKnowns = lastImportKnowns
        self.lastDowngradeLingqs = lastDowngradeLingqs
        self.itemSet = None

    def getConfig(self, name):
        return {
            "apiKey": self.apikey, 
            "languageCode": self.languageCode,
            "lastDeck": self.lastDeck,
            "lastImportKnowns": self.lastImportKnowns,
            "lastDowngradeLingqs": self.lastDowngradeLingqs
        }

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

    def test_should_get_default_level_to_interval(self, addonManager):
        result = Config(addonManager).GetLevelToInterval()
        assert result == {"new": 0, "recognized": 5, "familiar": 13, "learned": 34, "known": 85}

    def test_should_get_last_deck(self, addonManager):
        result = Config(addonManager).GetLastDeck()
        assert result == ""

    def test_should_get_last_import_knowns(self, addonManager):
        result = Config(addonManager).GetLastImportKnowns()
        assert result == False

    def test_should_get_last_downgrade_lingqs(self, addonManager):
        result = Config(addonManager).GetLastDowngradeLingqs()
        assert result == False


class TestSets:
    def test_should_set_api_key(self, addonManager):
        Config(addonManager).SetApiKey("testSetApiKey")
        assert addonManager.itemSet["apiKey"] == "testSetApiKey"

    def test_should_set_language_code(self, addonManager):
        Config(addonManager).SetLanguageCode("testSetLanguageCode")
        assert addonManager.itemSet["languageCode"] == "testSetLanguageCode"

    def test_should_set_last_deck(self, addonManager):
        Config(addonManager).SetLastDeck("TestDeck")
        assert addonManager.itemSet["lastDeck"] == "TestDeck"

    def test_should_set_last_import_knowns(self, addonManager):
        Config(addonManager).SetLastImportKnowns(True)
        assert addonManager.itemSet["lastImportKnowns"] == True

    def test_should_set_last_downgrade_lingqs(self, addonManager):
        Config(addonManager).SetLastDowngradeLingqs(True)
        assert addonManager.itemSet["lastDowngradeLingqs"] == True
