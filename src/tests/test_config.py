import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lingqAnkiSync"))

import Config


def test_getApiKey():
    config = Config.Config({"apiKey": "testApiKey"})
    assert config.getApiKey() == "testApiKey"
    
def test_GetEmptyApiKey():
    config = Config.Config({"apiKey": ""})
    assert config.getApiKey() == ""
    
def test_GetNoneApiKey():
    config = Config.Config({"apiKey": None})
    assert config.getApiKey() == ""

def test_GetLanguageCode():
    config = Config.Config({"languageCode": "testLanguageCode"})
    assert config.getLanguageCode() == "testLanguageCode"

def test_GetEmptyLanguageCode():
    config = Config.Config({"languageCode": ""})
    assert config.getLanguageCode() == ""

def test_GetNoneLanguageCode():
    config = Config.Config({"languageCode": None})
    assert config.getLanguageCode() == ""