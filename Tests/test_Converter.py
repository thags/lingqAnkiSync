import sys, os

sys.path.append(os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync"))
import Converter
from Models import Lingq, AnkiCard
import pytest


@pytest.fixture
def status_to_interval():
    return {"new": 100, "recognized": 200, "familiar": 300, "learned": 400, "known": 500}


class TestIntervalToStatus:
    def test_convert_anki_interval_to_lingq_status(self, status_to_interval):
        testInterval = 225
        resultStatus = Converter._anki_interval_to_lingq_status(testInterval, status_to_interval)
        assert resultStatus == "recognized"

    def test_should_return_max_status_if_interval_is_greater_than_max_interval(
        self, status_to_interval
    ):
        testInterval = 600
        resultStatus = Converter._anki_interval_to_lingq_status(testInterval, status_to_interval)
        assert resultStatus == "known"

    def test_should_return_min_status_if_interval_is_less_than_min_interval(
        self, status_to_interval
    ):
        testInterval = 50
        resultStatus = Converter._anki_interval_to_lingq_status(testInterval, status_to_interval)
        assert resultStatus == "new"


class TestStatusToInterval:
    def test_convert_lingq_status_to_anki_interval(self, status_to_interval):
        test_status = 2
        test_extended_status = 0
        result_status = Converter._lingq_status_to_anki_interval(
            test_status, test_extended_status, status_to_interval
        )
        assert result_status >= 300
        assert result_status <= 400

    def test_should_return_max_interval_plus_other_intervals_if_status_is_max_status(
        self, status_to_interval
    ):
        test_status = 3
        test_extended_status = 3
        result_status = Converter._lingq_status_to_anki_interval(
            test_status, test_extended_status, status_to_interval
        )
        assert result_status >= 500

    def test_should_return_min_interval_if_status_min_status(self, status_to_interval):
        test_status = 0
        test_extended_status = 0
        result_status = Converter._lingq_status_to_anki_interval(
            test_status, test_extended_status, status_to_interval
        )
        assert result_status >= 0
        assert result_status <= 100


class TestLingqInternalStatusConversion:
    def test_convert_lingq_internal_status_to_status(self):
        result_status = Converter.lingq_internal_status_to_status(
            internal_status=0, extended_status=None
        )
        assert result_status == Lingq.Lingq.LEVEL_1

        result_status2 = Converter.lingq_internal_status_to_status(
            internal_status=2, extended_status=0
        )
        assert result_status2 == Lingq.Lingq.LEVEL_3

        result_status3 = Converter.lingq_internal_status_to_status(
            internal_status=3, extended_status=3
        )
        assert result_status3 == Lingq.Lingq.LEVEL_KNOWN

        with pytest.raises(ValueError, match="accepted range"):
            Converter.lingq_internal_status_to_status(internal_status=1, extended_status=555)

    def test_ConvertLingqStatusToInternalStatus(self, status_to_interval):
        result_internal_status, result_external_status = Converter.lingq_status_to_internal_status(
            status=Lingq.Lingq.LEVEL_1
        )
        assert result_internal_status == 0
        assert result_external_status in (0, None)

        result_internal_status2, result_external_status2 = Converter.lingq_status_to_internal_status(
            status=Lingq.Lingq.LEVEL_3
        )
        assert result_internal_status2 == 2
        assert result_external_status2 == 0

        result_internal_status3, result_external_status3 = Converter.lingq_status_to_internal_status(
            status=Lingq.Lingq.LEVEL_KNOWN
        )
        assert result_internal_status3 == 3
        assert result_external_status3 == 3

        with pytest.raises(ValueError, match="No such status"):
            Converter.lingq_status_to_internal_status(status="understood")

        with pytest.raises(ValueError, match="No such status"):
            Converter.lingq_status_to_internal_status(status=1)


@pytest.fixture
def model_card():
    return AnkiCard.AnkiCard(
        1, "word", ["translation", "translation2"], 100, "new", ["tag1", "tag2"], "sentence", 0
    )


@pytest.fixture
def model_lingq():
    return Lingq.Lingq(
        1, "word", ["translation", "translation2"], 0, None, ["tag1", "tag2"], "sentence", 0
    )


class TestConvertAnkiToLingq:
    def test_should_convert_anki_card_to_lingq(self, status_to_interval, model_card):
        result_lingq = Converter.anki_cards_to_lingqs([model_card], status_to_interval)[0]
        assert result_lingq.primary_key == model_card.primary_key
        assert result_lingq.word == model_card.word
        assert result_lingq.translations == model_card.translations
        assert result_lingq.status == 0
        assert result_lingq.extended_status == 0
        assert result_lingq.tags == model_card.tags
        assert result_lingq.fragment == model_card.sentence
        assert result_lingq.importance == model_card.importance


class TestConvertLingqToAnki:
    def test_should_convert_lingq_to_anki_card(self, status_to_interval, model_card, model_lingq):
        result_anki_card = Converter.lingqs_to_anki_cards([model_lingq], status_to_interval)[0]
        assert result_anki_card.primary_key == model_lingq.primary_key
        assert result_anki_card.word == model_lingq.word
        assert result_anki_card.translations == model_lingq.translations
        assert result_anki_card.interval >= 0
        assert result_anki_card.interval <= 100
        assert result_anki_card.status == "new"
        assert result_anki_card.tags == model_lingq.tags
        assert result_anki_card.sentence == model_lingq.fragment
        assert result_anki_card.importance == model_lingq.importance
