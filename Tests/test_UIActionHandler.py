import pytest
from unittest.mock import Mock, patch, MagicMock
from lingqAnkiSync.UIActionHandler import ActionHandler
from lingqAnkiSync.Models.AnkiCard import AnkiCard
from lingqAnkiSync.Models.Lingq import Lingq

class TestUIActionHandler:
    @pytest.fixture
    def mock_addon_manager(self):
        """Mock addon manager for Config initialization."""
        mock_manager = Mock()
        # Provide realistic config data instead of empty dict
        mock_config = {"apiKey": "test_api_key", "languageCode": "es"}
        mock_manager.getConfig.return_value = mock_config
        mock_manager.writeConfig.return_value = None
        return mock_manager

    @pytest.fixture
    def sample_anki_cards(self):
        return [
            AnkiCard(
                primary_key=12345,
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
                primary_key=67890,
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
                primary_key=11111,
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
                primary_key=22222,
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
    def sample_status_to_interval(self):
        return {"new": 0, "recognized": 5, "familiar": 10, "learned": 25, "known": 50}

    @pytest.fixture
    def action_handler(self, mock_addon_manager, sample_status_to_interval):
        handler = ActionHandler(mock_addon_manager)
        with patch.object(
            handler.config, "get_status_to_interval", return_value=sample_status_to_interval
        ):
            yield handler

    @pytest.fixture
    def update_counts(self):
        return {"increased": 105, "decreased": 68, "api_updates": 166}

    def test_prep_cards_for_update_only_increase(
        self, action_handler, sample_anki_cards, sample_status_to_interval
    ):
        cards_to_increase, cards_to_decrease = action_handler._prep_cards_for_update(
            sample_anki_cards, sample_status_to_interval, downgrade=False
        )
        assert len(cards_to_increase) == 2
        assert len(cards_to_decrease) == 0  # No downgrades when downgrade=False

        words = [card.word for card in cards_to_increase]
        assert "hola" in words
        assert "gracias" not in words

        # Check status increased one level on 'casa' card
        assert "learned" in [card.status for card in cards_to_increase if card.word == "casa"]

    def test_prep_cards_for_update_increase_and_decrease(
        self, action_handler, sample_anki_cards, sample_status_to_interval
    ):
        cards_to_increase, cards_to_decrease = action_handler._prep_cards_for_update(
            sample_anki_cards, sample_status_to_interval, downgrade=True
        )
        assert len(cards_to_increase) == 2
        assert len(cards_to_decrease) == 1

        increase_words = [card.word for card in cards_to_increase]
        assert "hola" in increase_words
        assert "gracias" not in increase_words

        decrease_words = [card.word for card in cards_to_decrease]
        assert "mundo" in decrease_words
        assert "gracias" not in decrease_words

        assert "learned" in [card.status for card in cards_to_increase if card.word == "casa"]

    def test_integration_sync_with_real_mocks(
        self, action_handler, mock_lingq_server, mock_mw, update_counts
    ):
        """Integration test using real mock json data."""
        deck_name = "mock_deck"

        # Test a specific card: "acomodado" with pk 464263538
        test_card_pk = 464263538
        initial_lingq_card = mock_lingq_server.get_card_by_pk("es", test_card_pk)
        initial_anki_card = next(card_data for card_data in mock_mw.col._data["mock_deck"]["cards"] if card_data["primary_key"] == test_card_pk)
        
        assert initial_anki_card["status"] == "learned"
        assert initial_anki_card["interval"] == 100
        assert initial_lingq_card["status"] == 3
        assert initial_lingq_card["extended_status"] == 0

        increased, decreased, api_updates = action_handler.sync_lingq_status_to_lingq(
            deck_name, downgrade=True
        )

        final_lingq_card = mock_lingq_server.get_card_by_pk("es", test_card_pk)
        final_anki_card = next(card_data for card_data in mock_mw.col._data["mock_deck"]["cards"] if card_data["primary_key"] == test_card_pk)
        
        # Verify the card was updated in both databases
        assert final_lingq_card["status"] == 3
        assert final_lingq_card["extended_status"] == 3
        assert final_anki_card["status"] == "known"

        # Verify counts of cards calculated as needing to update
        # These counts are subject to change as the mock data is updated
        assert increased == update_counts["increased"]
        assert decreased == update_counts["decreased"]
        # This number does not match the number of `increased` and `decreased`
        # because some cards are not updated due to the status in anki already being
        # the same as the status in lingq
        assert api_updates == update_counts["api_updates"]

    def test_integration_sync_with_real_mocks_different_status_to_interval(
        self, action_handler, mock_lingq_server, mock_mw, sample_status_to_interval, update_counts
    ):
        """Integration test using real mock json data with different status to interval."""
        deck_name = "mock_deck"

        # Copy the sample status_to_interval but make it slightly different
        mock_get_status_to_interval = {k: v + 3 for k, v in sample_status_to_interval.items()}
        mock_get_status_to_interval["new"] = 0

        with patch.object(
            action_handler.config,
            "get_status_to_interval",
            return_value=mock_get_status_to_interval,
        ):
            increased, decreased, api_updates = action_handler.sync_lingq_status_to_lingq(
                deck_name, downgrade=True
            )

            # We are checking that the values are different because the status to interval is different
            assert increased != update_counts["increased"]
            assert decreased != update_counts["decreased"]
            assert api_updates != update_counts["api_updates"]
