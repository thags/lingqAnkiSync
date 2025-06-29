import LingqAnkiSync.Converter as Converter
from LingqAnkiSync.Models import Lingq, AnkiCard
import pytest


@pytest.fixture
def statusToInterval():
    return {"new": 100, "recognized": 200, "familiar": 300, "learned": 400, "known": 500}


class TestIntervalToStatus:
    def test_convert_anki_interval_to_lingq_status(self, statusToInterval):
        testInterval = 225
        resultStatus = Converter._AnkiIntervalToLingqStatus(testInterval, statusToInterval)
        assert resultStatus == "recognized"

    def test_should_return_max_status_if_interval_is_greater_than_max_interval(
        self, statusToInterval
    ):
        testInterval = 600
        resultStatus = Converter._AnkiIntervalToLingqStatus(testInterval, statusToInterval)
        assert resultStatus == "known"

    def test_should_return_min_status_if_interval_is_less_than_min_interval(
        self, statusToInterval
    ):
        testInterval = 50
        resultStatus = Converter._AnkiIntervalToLingqStatus(testInterval, statusToInterval)
        assert resultStatus == "new"

    def test_should_return_min_status_if_interval_is_equal_to_min_interval(
        self, statusToInterval
    ):
        testInterval = 100
        resultStatus = Converter._AnkiIntervalToLingqStatus(testInterval, statusToInterval)
        assert resultStatus == "new"


class TestStatusToInterval:
    def test_convert_lingq_status_to_anki_interval(self, statusToInterval):
        testStatus = 2
        testExtendedStatus = 0
        resultStatus = Converter._LingqStatusToAnkiInterval(
            testStatus, testExtendedStatus, statusToInterval
        )
        assert resultStatus >= 300
        assert resultStatus <= 400

    def test_should_return_max_interval_plus_other_intervals_if_status_is_max_status(
        self, statusToInterval
    ):
        testStatus = 3
        testExtendedStatus = 3
        resultStatus = Converter._LingqStatusToAnkiInterval(
            testStatus, testExtendedStatus, statusToInterval
        )
        assert resultStatus >= 500

    def test_should_return_min_interval_if_status_min_status(self, statusToInterval):
        testStatus = 0
        testExtendedStatus = 0
        resultStatus = Converter._LingqStatusToAnkiInterval(
            testStatus, testExtendedStatus, statusToInterval
        )
        assert resultStatus >= 0
        assert resultStatus <= 100


class TestLingqInternalStatusConversion:
    def test_convert_lingq_internal_status_to_status(self):
        resultStatus = Converter.LingqInternalStatusToStatus(
            internalStatus=0, extendedStatus=None
        )
        assert resultStatus == "new"

        resultStatus2 = Converter.LingqInternalStatusToStatus(
            internalStatus=2, extendedStatus=0
        )
        assert resultStatus2 == "familiar"

        resultStatus3 = Converter.LingqInternalStatusToStatus(
            internalStatus=3, extendedStatus=3
        )
        assert resultStatus3 == "known"

        with pytest.raises(ValueError, match="accepted range"):
            Converter.LingqInternalStatusToStatus(internalStatus=1, extendedStatus=555)

    def test_ConvertLingqStatusToInternalStatus(self, statusToInterval):
        resultInternalStatus, resultExternalStatus = Converter.LingqStatusToInternalStatus(
            status="new"
        )
        assert resultInternalStatus == 0
        assert resultExternalStatus in (0, None)

        (
            resultInternalStatus2,
            resultExternalStatus2,
        ) = Converter.LingqStatusToInternalStatus(status="familiar")
        assert resultInternalStatus2 == 2
        assert resultExternalStatus2 == 0

        (
            resultInternalStatus3,
            resultExternalStatus3,
        ) = Converter.LingqStatusToInternalStatus(status="known")
        assert resultInternalStatus3 == 3
        assert resultExternalStatus3 == 3

        with pytest.raises(ValueError, match="No such status"):
            Converter.LingqStatusToInternalStatus(status="understood")

        with pytest.raises(ValueError, match="No such status"):
            Converter.LingqStatusToInternalStatus(status=1)


@pytest.fixture
def modelCard():
    return AnkiCard.AnkiCard(
        1, "word", ["translation", "translation2"], 100, "new", ["tag1", "tag2"], "sentence", 0
    )


@pytest.fixture
def modelLingq():
    return Lingq.Lingq(
        1, "word", ["translation", "translation2"], 0, None, ["tag1", "tag2"], "sentence", 0
    )


class TestConvertAnkiToLingq:
    def test_convert_anki_card_to_lingq(self, statusToInterval, modelCard):
        resultLingq = Converter.AnkiCardsToLingqs([modelCard], statusToInterval)[0]
        assert resultLingq.primaryKey == modelCard.primaryKey
        assert resultLingq.word == modelCard.word
        assert resultLingq.translations == modelCard.translations
        assert resultLingq.status == 0
        assert resultLingq.extendedStatus == 0
        assert resultLingq.tags == modelCard.tags
        assert resultLingq.fragment == modelCard.sentence
        assert resultLingq.importance == modelCard.importance


class TestConvertLingqToAnki:
    def test_convert_lingq_to_anki_card(self, statusToInterval, modelLingq):
        resultAnkiCard = Converter.LingqsToAnkiCards([modelLingq], statusToInterval)[0]
        assert resultAnkiCard.primaryKey == modelLingq.primaryKey
        assert resultAnkiCard.word == modelLingq.word
        assert resultAnkiCard.translations == modelLingq.translations
        assert resultAnkiCard.interval >= 0
        assert resultAnkiCard.interval <= 100
        assert resultAnkiCard.status == "new"
        assert resultAnkiCard.tags == modelLingq.tags
        assert resultAnkiCard.sentence == modelLingq.fragment
        assert resultAnkiCard.importance == modelLingq.importance


class TestCardCanIncreaseStatus:
    def test_should_return_true_if_interval_is_greater_than_threshold(
        self, statusToInterval, modelCard
    ):
        modelCard.interval = 250
        modelCard.status = "recognized"
        result = Converter.CardCanIncreaseStatus(modelCard, statusToInterval)
        assert result

    def test_should_return_false_if_interval_is_equal_to_threshold(
        self, statusToInterval, modelCard
    ):
        modelCard.interval = 200
        modelCard.status = "recognized"
        result = Converter.CardCanIncreaseStatus(modelCard, statusToInterval)
        assert not result

    def test_should_return_false_if_interval_is_less_than_threshold(
        self, statusToInterval, modelCard
    ):
        modelCard.interval = 150
        modelCard.status = "recognized"
        result = Converter.CardCanIncreaseStatus(modelCard, statusToInterval)
        assert not result

    def test_should_return_false_for_new_card(self, modelCard, statusToInterval):
        modelCard.interval = 0
        modelCard.status = "new"
        result = Converter.CardCanIncreaseStatus(modelCard, statusToInterval)
        assert not result

    def test_should_return_true_for_known_card_with_high_interval(
        self, modelCard, statusToInterval
    ):
        modelCard.interval = 1000
        modelCard.status = "known"
        result = Converter.CardCanIncreaseStatus(modelCard, statusToInterval)
        assert result
