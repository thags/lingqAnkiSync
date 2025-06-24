import pytest
from unittest.mock import Mock, patch, MagicMock
from LingqAnkiSync.UIActionHandler import ActionHandler
from LingqAnkiSync.Models.AnkiCard import AnkiCard
from LingqAnkiSync.Models.Lingq import Lingq


class TestUIActionHandler:
    @pytest.fixture
    def mockAddonManager(self):
        """Mock addon manager for Config initialization."""
        mockManager = Mock()
        # Provide realistic config data instead of empty dict
        mockConfig = {"apiKey": "test_api_key", "languageCode": "es"}
        mockManager.getConfig.return_value = mockConfig
        mockManager.writeConfig.return_value = None
        return mockManager

    @pytest.fixture
    def sampleAnkiCards(self):
        return [
            AnkiCard(
                primaryKey=12345,
                word="hola",
                translations=["hello"],
                interval=10,  # Should trigger status increase
                status="new",
                tags=["tag1"],
                sentence="Hola mundo",
                importance=3,
                popularity=5,
            ),
            AnkiCard(
                primaryKey=67890,
                word="mundo",
                translations=["world"],
                interval=2,  # Should trigger downgrade
                status="recognized",
                tags=["tag2"],
                sentence="Hola mundo",
                importance=2,
                popularity=3,
            ),
            AnkiCard(
                primaryKey=11111,
                word="casa",
                translations=["house"],
                interval=300,  # Very high interval should still only trigger single status increase
                status="familiar",
                tags=["tag3"],
                sentence="Mi casa es grande",
                importance=4,
                popularity=7,
            ),
            AnkiCard(
                primaryKey=22222,
                word="gracias",
                translations=["thank you"],
                interval=10,  # No status increase
                status="recognized",
                tags=["tag4"],
                sentence="Muchas gracias",
                importance=3,
                popularity=8,
            ),
        ]

    @pytest.fixture
    def sampleStatusToInterval(self):
        return {"new": 0, "recognized": 5, "familiar": 10, "learned": 25, "known": 50}

    @pytest.fixture
    def actionHandler(self, mockAddonManager, sampleStatusToInterval):
        handler = ActionHandler(mockAddonManager)
        with patch.object(
            handler.config, "GetStatusToInterval", return_value=sampleStatusToInterval
        ):
            yield handler

    @pytest.fixture
    def updateCounts(self):
        return {"increased": 105, "decreased": 68, "api_updates": 166}

    def test_prep_cards_for_update_only_increase(
        self, actionHandler, sampleAnkiCards, sampleStatusToInterval
    ):
        cardsToIncrease, cardsToDecrease = actionHandler._PrepCardsForUpdate(
            sampleAnkiCards, sampleStatusToInterval, downgrade=False
        )
        assert len(cardsToIncrease) == 2
        assert len(cardsToDecrease) == 0  # No downgrades when downgrade=False

        words = [card.word for card in cardsToIncrease]
        assert "hola" in words
        assert "gracias" not in words

        # Check status increased one level on 'casa' card
        assert "learned" in [card.status for card in cardsToIncrease if card.word == "casa"]

    def test_prep_cards_for_update_increase_and_decrease(
        self, actionHandler, sampleAnkiCards, sampleStatusToInterval
    ):
        cardsToIncrease, cardsToDecrease = actionHandler._PrepCardsForUpdate(
            sampleAnkiCards, sampleStatusToInterval, downgrade=True
        )
        assert len(cardsToIncrease) == 2
        assert len(cardsToDecrease) == 1

        increaseWords = [card.word for card in cardsToIncrease]
        assert "hola" in increaseWords
        assert "gracias" not in increaseWords

        decreaseWords = [card.word for card in cardsToDecrease]
        assert "mundo" in decreaseWords
        assert "gracias" not in decreaseWords

        assert "learned" in [card.status for card in cardsToIncrease if card.word == "casa"]

    def test_integration_sync_with_real_mocks(
        self, actionHandler, mockLingqServer, mockMw, updateCounts
    ):
        """Integration test using real mock json data."""
        deckName = "mock_deck"

        # Test a specific card: "acomodado" with pk 464263538
        testCardPk = 464263538
        initialLingqCard = mockLingqServer.get_card_by_pk("es", testCardPk)
        initialAnkiCard = next(
            cardData
            for cardData in mockMw.col._data["mock_deck"]["cards"]
            if cardData["primary_key"] == testCardPk
        )

        assert initialAnkiCard["status"] == "learned"
        assert initialAnkiCard["interval"] == 100
        assert initialLingqCard["status"] == 3
        assert initialLingqCard["extended_status"] == 0

        increased, decreased, apiUpdates = actionHandler.SyncLingqStatusToLingq(
            deckName, downgrade=True
        )

        finalLingqCard = mockLingqServer.get_card_by_pk("es", testCardPk)
        finalAnkiCard = next(
            cardData
            for cardData in mockMw.col._data["mock_deck"]["cards"]
            if cardData["primary_key"] == testCardPk
        )

        # Verify the card was updated in both databases
        assert finalLingqCard["status"] == 3
        assert finalLingqCard["extended_status"] == 3
        assert finalAnkiCard["status"] == "known"

        # Verify counts of cards calculated as needing to update
        # These counts are subject to change as the mock data is updated
        assert increased == updateCounts["increased"]
        assert decreased == updateCounts["decreased"]
        # This number does not match the number of `increased` and `decreased`
        # because some cards are not updated due to the status in anki already being
        # the same as the status in lingq
        assert apiUpdates == updateCounts["api_updates"]

    def test_integration_sync_with_real_mocks_different_status_to_interval(
        self, actionHandler, mockLingqServer, mockMw, sampleStatusToInterval, updateCounts
    ):
        """Integration test using real mock json data with different status to interval."""
        deckName = "mock_deck"

        # Copy the sample status_to_interval but make it slightly different
        mockGetStatusToInterval = {k: v + 3 for k, v in sampleStatusToInterval.items()}
        mockGetStatusToInterval["new"] = 0

        with patch.object(
            actionHandler.config,
            "GetStatusToInterval",
            return_value=mockGetStatusToInterval,
        ):
            increased, decreased, apiUpdates = actionHandler.SyncLingqStatusToLingq(
                deckName, downgrade=True
            )

            # We are checking that the values are different because the status to interval is different
            assert increased != updateCounts["increased"]
            assert decreased != updateCounts["decreased"]
            assert apiUpdates != updateCounts["api_updates"]
