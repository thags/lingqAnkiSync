from utils.Config import Config


def test_getApiKey():
    config = Config({"apiKey": "testApiKey"})
    assert config.getApiKey() == "testApiKey"
    
def test_GetEmptyApiKey():
    config = Config({"apiKey": ""})
    assert config.getApiKey() == ""
    
def test_GetNoneApiKey():
    config = Config({"apiKey": None})
    assert config.getApiKey() == ""

def test_GetLanguageCode():
    config = Config({"languageCode": "testLanguageCode"})
    assert config.getLanguageCode() == "testLanguageCode"

def test_GetEmptyLanguageCode():
    config = Config({"languageCode": ""})
    assert config.getLanguageCode() == ""

def test_GetNoneLanguageCode():
    config = Config({"languageCode": None})
    assert config.getLanguageCode() == ""
    
def test_GetStatusToInterval():
    config = Config({"statusToInterval": "{0: 0, 1: 5, 2: 10, 3: 20, 4: 40}"})
    assert config.getStatusToInterval() == "{0: 0, 1: 5, 2: 10, 3: 20, 4: 40}"