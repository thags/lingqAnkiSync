import sys, os
sys.path.append(
    os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync")
)
from Config import Config

class configRepo:
    def __init__(self):
        self.apikey = 'testApiKey'
        self.languageCode = 'testLanguageCode'
        self.itemSet = None
    
    def getConfig(self, name):
        return {"apiKey": self.apikey, "languageCode": self.languageCode}
    
    def writeConfig(self, name, setTo):
        self.itemSet = setTo

class TestGets:
    def test_should_get_api_key(self):
        addonManager = configRepo()
        result = Config(addonManager).GetApiKey()
        assert result == 'testApiKey'
        
    def test_should_get_language_code(self):
        addonManager = configRepo()
        result = Config(addonManager).GetLanguageCode()
        assert result == 'testLanguageCode'
    
    def test_should_get_deafult_status_to_interval(self):
        addonManager = configRepo()
        result = Config(addonManager).GetStatusToInterval()
        assert result == {0: 1, 1: 5, 2: 10, 3: 20, 4: 40}
        
class TestSets:
    def test_should_set_api_key(self):
        addonManager = configRepo()
        Config(addonManager).SetApiKey('testSetApiKey')
        assert addonManager.itemSet['apiKey'] == 'testSetApiKey'
    
    def test_should_set_language_code(self):
        addonManager = configRepo()
        Config(addonManager).SetLanguageCode('testSetLanguageCode')
        assert addonManager.itemSet['languageCode'] == 'testSetLanguageCode'