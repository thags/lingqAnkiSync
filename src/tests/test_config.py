from utils.Config import Config

class testConfig:
    def __init__(self, configToReturn):
        self.configToReturn = configToReturn

    def getConfig(self, configName):
        return self.configToReturn

def test_should_get_apiKey():
    config = Config(testConfig({"apiKey": "testApiKey"}))
    assert config.GetApiKey() == "testApiKey"
    
def test_should_get_empty_string_apiKey():
    config = Config(testConfig({"apiKey": ""}))
    assert config.GetApiKey() == ""
    
def test_should_return_empty_string_on_none_apiKey():
    config = Config(testConfig({"apiKey": None}))
    assert config.GetApiKey() == ""

def test_should_get_languageCode():
    config = Config(testConfig({"languageCode": "testLanguageCode"}))
    assert config.GetLanguageCode() == "testLanguageCode"

def test_should_get_empty_string_languageCode():
    config = Config(testConfig({"languageCode": ""}))
    assert config.GetLanguageCode() == ""

def test_should_return_empty_string_on_none_languageCode():
    config = Config(testConfig({"languageCode": None}))
    assert config.GetLanguageCode() == ""
    
def test_should_get_statusToInterval():
    config = Config(testConfig({"statusToInterval": "{0: 0, 1: 5, 2: 10, 3: 20, 4: 40}"}))
    assert config.GetStatusToInterval() == "{0: 0, 1: 5, 2: 10, 3: 20, 4: 40}"