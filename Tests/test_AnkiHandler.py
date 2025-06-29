import pytest
from LingqAnkiSync import AnkiHandler
from LingqAnkiSync.Models.AnkiCard import AnkiCard
from LingqAnkiSync.Models.Lingq import Lingq


@pytest.fixture
def sampleAnkiCard():
    return AnkiCard(
        primaryKey=12345,
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
def sampleLingq():
    return Lingq(
        primaryKey=12345,
        word="test_word",
        translations=["test_translation"],
        status=0,
        extendedStatus=0,
        tags=["tag1"],
        fragment="This is a test sentence.",
        importance=3,
    )


class TestDoesDuplicateCardExistInDeck:
    def test_card_exists(self, mockMw):
        # Use a primary key that exists in the mock data
        assert AnkiHandler.DoesDuplicateCardExistInDeck(107856432, "mock_deck")

    def test_card_does_not_exist(self, mockMw):
        assert not AnkiHandler.DoesDuplicateCardExistInDeck(999999999, "mock_deck")

    def test_deck_does_not_exist(self, mockMw):
        assert not AnkiHandler.DoesDuplicateCardExistInDeck(107856432, "NonExistentDeck")


class TestCreateNote:
    def test_create_note_success(self, mockMw, sampleAnkiCard):
        # Ensure the card doesn't exist before we add it
        assert not AnkiHandler.DoesDuplicateCardExistInDeck(
            sampleAnkiCard.primaryKey, "mock_deck"
        )
        assert AnkiHandler.CreateNote(sampleAnkiCard, "mock_deck", "es")
        # Check card exists now
        assert AnkiHandler.DoesDuplicateCardExistInDeck(
            sampleAnkiCard.primaryKey, "mock_deck"
        )

    def test_create_note_fails_when_duplicate_exists(self, mockMw, sampleAnkiCard):
        # Use a primary key that already exists in the mock data
        sampleAnkiCard.primaryKey = 107856432
        assert not AnkiHandler.CreateNote(sampleAnkiCard, "mock_deck", "es")


class TestCreateNotesFromCards:
    def test_create_multiple_notes(self, mockMw):
        cards = [
            AnkiCard(
                primaryKey=888888888,
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
                primaryKey=777777777,
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

        assert AnkiHandler.CreateNotesFromCards(cards, "mock_deck", "es") == 2
        assert AnkiHandler.DoesDuplicateCardExistInDeck(cards[0].primaryKey, "mock_deck")
        assert AnkiHandler.DoesDuplicateCardExistInDeck(cards[1].primaryKey, "mock_deck")

    def test_create_notes_with_duplicates(self, mockMw):
        cards = [
            AnkiCard(
                primaryKey=107856432,  # This exists in mock data
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
                primaryKey=666666666,  # This is new to the mock data
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

        assert AnkiHandler.DoesDuplicateCardExistInDeck(cards[0].primaryKey, "mock_deck")
        assert not AnkiHandler.DoesDuplicateCardExistInDeck(cards[1].primaryKey, "mock_deck")

        assert AnkiHandler.CreateNotesFromCards(cards, "mock_deck", "es") == 1

        # Double-check database contains both cards now
        assert AnkiHandler.DoesDuplicateCardExistInDeck(cards[0].primaryKey, "mock_deck")
        assert AnkiHandler.DoesDuplicateCardExistInDeck(cards[1].primaryKey, "mock_deck")
