import sys, os
sys.path.append(
    os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync")
)
from Converter import ConvertAnkiCardsToLingqs, _ConvertAnkiIntervalToLingqStatus, _ConvertLingqStatusToAnkiInterval
from Models import Lingq, AnkiCard
import pytest

class TestIntervalToStatus:
    def test_ConvertAnkiIntervalToLingqStatus(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        testInterval = 225
        resultStatus = _ConvertAnkiIntervalToLingqStatus(testInterval, testStatusToInterval)
        assert resultStatus == 2

    def test_should_return_max_status_if_interval_is_greater_than_max_interval(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        testInterval = 600
        resultStatus = _ConvertAnkiIntervalToLingqStatus(testInterval, testStatusToInterval)
        assert resultStatus == 4
    
    def test_should_return_min_status_if_interval_is_less_than_min_interval(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        testInterval = 50
        resultStatus = _ConvertAnkiIntervalToLingqStatus(testInterval, testStatusToInterval)
        assert resultStatus == 0

class TestStatusToInterval:
    def test_ConvertLingqStatusToAnkiInterval(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        testStatus = 2
        resultStatus = _ConvertLingqStatusToAnkiInterval(testStatus, testStatusToInterval)
        assert resultStatus == 300

    def test_should_return_max_interval_if_status_is_greater_than_max_status(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        testStatus = 5
        resultStatus = _ConvertLingqStatusToAnkiInterval(testStatus, testStatusToInterval)
        assert resultStatus == 500
    
    def test_should_return_min_interval_if_status_is_less_than_min_stats(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        testStatus = -1
        resultStatus = _ConvertLingqStatusToAnkiInterval(testStatus, testStatusToInterval)
        assert resultStatus == 100
        
class TestConvertAnkiToLingq:
    def test_should_convert_ankiCard_to_Lingq(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        ankiCard = AnkiCard.AnkiCard(1, "word", "translation", 100)
        modelLingq = Lingq.Lingq(1, "word", "translation", 0, None)

        resultLingq = ConvertAnkiCardsToLingqs([ankiCard], testStatusToInterval)[0]
        assert resultLingq.primaryKey == modelLingq.primaryKey
        assert resultLingq.word == modelLingq.word
        assert resultLingq.translation == modelLingq.translation
        assert resultLingq.status == modelLingq.status
        assert resultLingq.extended_status is None
        
class TestConvertLingqToAnki:
    def test_should_convert_Lingq_to_AnkiCard(self):
        testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
        ankiCard = AnkiCard.AnkiCard(1, "word", "translation", 100)
        modelLingq = Lingq.Lingq(1, "word", "translation", 0, None)

        resultLingq = ConvertAnkiCardsToLingqs([ankiCard], testStatusToInterval)[0]
        assert resultLingq.primaryKey == modelLingq.primaryKey
        assert resultLingq.word == modelLingq.word
        assert resultLingq.translation == modelLingq.translation
        assert resultLingq.status == modelLingq.status
        assert resultLingq.extended_status is None