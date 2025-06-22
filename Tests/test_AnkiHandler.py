import pytest
from unittest.mock import MagicMock

from lingqAnkiSync import AnkiHandler
from lingqAnkiSync.Models.AnkiCard import AnkiCard
from lingqAnkiSync.Models.Lingq import Lingq


@pytest.fixture
def sample_anki_card():
    return AnkiCard(
        primary_key=12345,
        word="test_word",
        translations=["test_translation"],
        interval=5,
        status="recognized",
        tags=["tag1"],
        sentence="This is a test sentence.",
        importance=3,
        popularity=0,
    )


@pytest.fixture
def sample_lingq():
    return Lingq(
        primary_key=12345,
        word="test_word",
        translations=["test_translation"],
        status=0,
        extended_status=0,
        tags=["tag1"],
        fragment="This is a test sentence.",
        importance=3,
    )


class TestDoesDuplicateCardExistInDeck:
    def test_card_exists(self, mock_mw):
        # Use a primary key that exists in the mock data
        assert AnkiHandler.does_duplicate_card_exist_in_deck(107856432, "mock_deck")

    def test_card_does_not_exist(self, mock_mw):
        assert not AnkiHandler.does_duplicate_card_exist_in_deck(999999999, "mock_deck")

    def test_deck_does_not_exist(self, mock_mw):
        assert not AnkiHandler.does_duplicate_card_exist_in_deck(107856432, "NonExistentDeck")


class TestCreateNote:
    def test_create_note_success(self, mock_mw, sample_anki_card):
        # Ensure the card doesn't exist before we add it
        assert not AnkiHandler.does_duplicate_card_exist_in_deck(
            sample_anki_card.primary_key, "mock_deck"
        )
        # Check succesfful execution of create_note
        assert AnkiHandler.create_note(sample_anki_card, "mock_deck")
        # Check card exists now
        assert AnkiHandler.does_duplicate_card_exist_in_deck(
            sample_anki_card.primary_key, "mock_deck"
        )

    def test_create_note_fails_when_duplicate_exists(self, mock_mw, sample_anki_card):
        # Use a primary key that already exists in the mock data
        sample_anki_card.primary_key = 107856432
        assert not AnkiHandler.create_note(sample_anki_card, "mock_deck")


class TestCreateNotesFromCards:
    def test_create_multiple_notes(self, mock_mw):
        cards = [
            AnkiCard(
                primary_key=888888888,
                word="word1",
                translations=["translation1"],
                interval=0,
                status="new",
                tags=[],
                sentence="Sentence 1",
                importance=1,
                popularity=0,
            ),
            AnkiCard(
                primary_key=777777777,
                word="word2",
                translations=["translation2"],
                interval=5,
                status="recognized",
                tags=["tag1"],
                sentence="Sentence 2",
                importance=2,
                popularity=0,
            ),
        ]

        assert AnkiHandler.create_notes_from_cards(cards, "mock_deck") == 2
        assert AnkiHandler.does_duplicate_card_exist_in_deck(cards[0].primary_key, "mock_deck")
        assert AnkiHandler.does_duplicate_card_exist_in_deck(cards[1].primary_key, "mock_deck")

    def test_create_notes_with_duplicates(self, mock_mw):
        cards = [
            AnkiCard(
                primary_key=107856432,  # This exists in mock data
                word="existing_word",
                translations=["translation"],
                interval=0,
                status="new",
                tags=[],
                sentence="Sentence 1",
                importance=1,
                popularity=0,
            ),
            AnkiCard(
                primary_key=666666666,  # This is new to the mock data
                word="new_word",
                translations=["translation"],
                interval=0,
                status="new",
                tags=[],
                sentence="Sentence 2",
                importance=1,
                popularity=0,
            ),
        ]

        assert AnkiHandler.does_duplicate_card_exist_in_deck(cards[0].primary_key, "mock_deck")
        assert not AnkiHandler.does_duplicate_card_exist_in_deck(cards[1].primary_key, "mock_deck")

        assert AnkiHandler.create_notes_from_cards(cards, "mock_deck") == 1

        # Double-check database contains both cards now
        assert AnkiHandler.does_duplicate_card_exist_in_deck(cards[0].primary_key, "mock_deck")
        assert AnkiHandler.does_duplicate_card_exist_in_deck(cards[1].primary_key, "mock_deck")
