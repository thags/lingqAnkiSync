import sys, os

sys.path.append(os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync"))
from Config import Config
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
def addon_manager():
    return ConfigRepo("testApiKey", "testLanguageCode")


class TestGets:
    def test_should_get_api_key(self, addon_manager):
        result = Config(addon_manager).get_api_key()
        assert result == "testApiKey"

    def test_should_get_language_code(self, addon_manager):
        result = Config(addon_manager).get_language_code()
        assert result == "testLanguageCode"

    def test_should_get_deafult_status_to_interval(self, addon_manager):
        result = Config(addon_manager).get_status_to_interval()
        assert result == {"new": 0, "recognized": 5, "familiar": 13, "learned": 34, "known": 85}


class TestSets:
    def test_should_set_api_key(self, addon_manager):
        Config(addon_manager).set_api_key("testSetApiKey")
        assert addon_manager.itemSet["apiKey"] == "testSetApiKey"

    def test_should_set_language_code(self, addon_manager):
        Config(addon_manager).set_language_code("testSetLanguageCode")
        assert addon_manager.itemSet["languageCode"] == "testSetLanguageCode"
