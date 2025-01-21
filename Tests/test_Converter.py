import sys, os
sys.path.append(
    os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync")
)
import Converter
from Models import Lingq, AnkiCard
import pytest

@pytest.fixture
def status_to_interval():
    return {
        'new': 100,
        'recognized': 200,
        'familiar': 300,
        'learned': 400,
        'known': 500
    }

class TestIntervalToStatus:
    def test_ConvertAnkiIntervalToLingqStatus(self, status_to_interval):
        testInterval = 225
        resultStatus = Converter._AnkiIntervalToLingqStatus(testInterval, status_to_interval)
        assert resultStatus == 'recognized'

    def test_should_return_max_status_if_interval_is_greater_than_max_interval(self, status_to_interval):
        testInterval = 600
        resultStatus = Converter._AnkiIntervalToLingqStatus(testInterval, status_to_interval)
        assert resultStatus == 'known'

    def test_should_return_min_status_if_interval_is_less_than_min_interval(self, status_to_interval):
        testInterval = 50
        resultStatus = Converter._AnkiIntervalToLingqStatus(testInterval, status_to_interval)
        assert resultStatus == 'new'

class TestStatusToInterval:
    def test_ConvertLingqStatusToAnkiInterval(self, status_to_interval):
        testStatus = 2
        testExtendedStatus = 0
        resultStatus = Converter._LingqStatusToAnkiInterval(testStatus, testExtendedStatus, status_to_interval)
        assert resultStatus >= 300
        assert resultStatus <= 400

    def test_should_return_max_interval_plus_other_intervals_if_status_is_max_status(self, status_to_interval):
        testStatus = 3
        testExtendedStatus = 3
        resultStatus = Converter._LingqStatusToAnkiInterval(testStatus, testExtendedStatus, status_to_interval)
        assert resultStatus >= 500

    def test_should_return_min_interval_if_status_min_status(self, status_to_interval):
        testStatus = 0
        testExtendedStatus = 0
        resultStatus = Converter._LingqStatusToAnkiInterval(testStatus, testExtendedStatus, status_to_interval)
        assert resultStatus >= 0
        assert resultStatus <= 100

class TestLingqInternalStatusConversion:
    def test_ConvertLingqInternalStatusToStatus(self):
        resultStatus = Converter._LingqInternalStatusToStatus(internal_status=0, extended_status=None)
        assert resultStatus == Lingq.Lingq.LEVEL_1

        resultStatus2 = Converter._LingqInternalStatusToStatus(internal_status=2, extended_status=0)
        assert resultStatus2 == Lingq.Lingq.LEVEL_3

        resultStatus3 = Converter._LingqInternalStatusToStatus(internal_status=3, extended_status=3)
        assert resultStatus3 == Lingq.Lingq.LEVEL_KNOWN

        with pytest.raises(ValueError, match='accepted range'):
            Converter._LingqInternalStatusToStatus(internal_status=1, extended_status=555)

    def test_ConvertLingqStatusToInternalStatus(self, status_to_interval):
        resultInternalStatus, resultExternalStatus = Converter._LingqStatusToInternalStatus(status=Lingq.Lingq.LEVEL_1)
        assert resultInternalStatus == 0
        assert resultExternalStatus in (0, None)

        resultInternalStatus2, resultExternalStatus2 = Converter._LingqStatusToInternalStatus(status=Lingq.Lingq.LEVEL_3)
        assert resultInternalStatus2 == 2
        assert resultExternalStatus2 == 0

        resultInternalStatus3, resultExternalStatus3 = Converter._LingqStatusToInternalStatus(status=Lingq.Lingq.LEVEL_KNOWN)
        assert resultInternalStatus3 == 3
        assert resultExternalStatus3 == 3

        with pytest.raises(ValueError, match='No such status'):
            Converter._LingqStatusToInternalStatus(status='understood')

        with pytest.raises(ValueError, match='No such status'):
            Converter._LingqStatusToInternalStatus(status=1)


@pytest.fixture
def model_card():
    return AnkiCard.AnkiCard(1, "word", ["translation", "translation2"], 100, 'new', ["tag1", "tag2"], "sentence", 0)

@pytest.fixture
def model_lingq():
    return Lingq.Lingq(1, "word", ["translation", "translation2"], 0, None, ["tag1", "tag2"], "sentence", 0 )

class TestConvertAnkiToLingq:
    def test_should_convert_anki_card_to_lingq(self, status_to_interval, model_card):
        result_lingq = Converter.AnkiCardsToLingqs([model_card], status_to_interval)[0]
        assert result_lingq.primaryKey == model_card.primaryKey
        assert result_lingq.word == model_card.word
        assert result_lingq.translations == model_card.translations
        assert result_lingq.status == 0
        assert result_lingq.extended_status == 0
        assert result_lingq.tags == model_card.tags
        assert result_lingq.fragment == model_card.sentence
        assert result_lingq.importance == model_card.importance

class TestConvertLingqToAnki:
    def test_should_convert_Lingq_to_AnkiCard(self, status_to_interval, model_card, model_lingq):
        resultAnkiCard = Converter.LingqsToAnkiCards([model_lingq], status_to_interval)[0]
        assert resultAnkiCard.primaryKey == model_lingq.primaryKey
        assert resultAnkiCard.word == model_lingq.word
        assert resultAnkiCard.translations == model_lingq.translations
        assert resultAnkiCard.interval >= 0
        assert resultAnkiCard.interval <= 100
        assert resultAnkiCard.status == 'new'
        assert resultAnkiCard.tags == model_lingq.tags
        assert resultAnkiCard.sentence == model_lingq.fragment
        assert resultAnkiCard.importance == model_lingq.importance