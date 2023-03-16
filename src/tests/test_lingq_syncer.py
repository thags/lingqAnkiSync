from Lingq.src.LingqSyncer import LingqSyncer
from mock_examples.slow import slow

def test_should_update_lingq_status():
    lingqSyncer = LingqSyncer("testApiKey", "testLanguageCode")
    