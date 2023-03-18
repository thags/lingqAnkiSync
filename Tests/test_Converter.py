import sys, os
sys.path.append(
    os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync")
)
from Converter import ConvertAnkiCardsToLingqs, ConvertLingqsToAnkiCards, _ConvertAnkiIntervalToLingqStatus, _ConvertLingqStatusToAnkiInterval
from Models import Lingq, AnkiCard
import pytest

@pytest.fixture
def statusToInterval():
    return {0:100, 1:200, 2:300, 3:400, 4:500}

class TestIntervalToStatus:
    def test_ConvertAnkiIntervalToLingqStatus(self, statusToInterval):
        testInterval = 225
        resultStatus = _ConvertAnkiIntervalToLingqStatus(testInterval, statusToInterval)
        assert resultStatus == 2

    def test_should_return_max_status_if_interval_is_greater_than_max_interval(self, statusToInterval):
        testInterval = 600
        resultStatus = _ConvertAnkiIntervalToLingqStatus(testInterval, statusToInterval)
        assert resultStatus == 4
    
    def test_should_return_min_status_if_interval_is_less_than_min_interval(self, statusToInterval):
        testInterval = 50
        resultStatus = _ConvertAnkiIntervalToLingqStatus(testInterval, statusToInterval)
        assert resultStatus == 0

class TestStatusToInterval:
    def test_ConvertLingqStatusToAnkiInterval(self, statusToInterval):
        testStatus = 2
        resultStatus = _ConvertLingqStatusToAnkiInterval(testStatus, statusToInterval)
        assert resultStatus == 300

    def test_should_return_max_interval_if_status_is_greater_than_max_status(self, statusToInterval):
        testStatus = 5
        resultStatus = _ConvertLingqStatusToAnkiInterval(testStatus, statusToInterval)
        assert resultStatus == 500
    
    def test_should_return_min_interval_if_status_is_less_than_min_stats(self, statusToInterval):
        testStatus = -1
        resultStatus = _ConvertLingqStatusToAnkiInterval(testStatus, statusToInterval)
        assert resultStatus == 100
        
        
@pytest.fixture
def Modelankicard():
    return AnkiCard.AnkiCard(1, "word", "translation", 100)

@pytest.fixture
def Modellingq():
    return Lingq.Lingq(1, "word", "translation", 0, None)

class TestConvertAnkiToLingq:
    def test_should_convert_ankiCard_to_Lingq(self, statusToInterval, Modelankicard, Modellingq):
        resultLingq = ConvertAnkiCardsToLingqs([Modelankicard], statusToInterval)[0]
        assert resultLingq.primaryKey == Modellingq.primaryKey
        assert resultLingq.word == Modellingq.word
        assert resultLingq.translation == Modellingq.translation
        assert resultLingq.status == Modellingq.status
        assert resultLingq.extended_status is None
        
class TestConvertLingqToAnki:
    def test_should_convert_Lingq_to_AnkiCard(self, statusToInterval, Modelankicard, Modellingq):
        resultAnkiCard = ConvertLingqsToAnkiCards([Modellingq], statusToInterval)[0]
        assert resultAnkiCard.primaryKey == Modelankicard.primaryKey
        assert resultAnkiCard.word == Modelankicard.word
        assert resultAnkiCard.translation == Modelankicard.translation
        assert resultAnkiCard.interval == Modelankicard.interval