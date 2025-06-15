import pytest
import requests
import time
import math
from unittest.mock import patch
from lingqAnkiSync.LingqApi import LingqApi
from lingqAnkiSync.Models.Lingq import Lingq


class TestLingqApiMock:
    def test_get_cards_basic(self, mock_lingq_server):
        response = requests.get("https://www.lingq.com/api/v3/es/cards/")
        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert "results" in data
        assert isinstance(data["results"], list)
        assert data["count"] > 0

    def test_get_cards_pagination(self, mock_lingq_server):
        response1 = requests.get("https://www.lingq.com/api/v3/es/cards/?page=1&page_size=5")
        assert response1.status_code == 200

        data1 = response1.json()
        assert len(data1["results"]) <= 5
        assert len(data1["results"]) > 0

        response2 = requests.get("https://www.lingq.com/api/v3/es/cards/?page=2&page_size=5")
        assert response2.status_code == 200

        data2 = response2.json()
        # Verify pagination works by checking pages don't overlap
        if len(data1["results"]) > 0 and len(data2["results"]) > 0:
            page1_pks = {card["pk"] for card in data1["results"]}
            page2_pks = {card["pk"] for card in data2["results"]}
            assert page1_pks.isdisjoint(page2_pks), "Pages should not contain overlapping cards"

    def test_get_cards_status_filter(self, mock_lingq_server):
        # Get cards with status 0 (new)
        response = requests.get("https://www.lingq.com/api/v3/es/cards/?status=0&status=2")
        assert response.status_code == 200

        data = response.json()
        for card in data["results"]:
            assert (card["status"], card["extended_status"]) in [(0, 0), (2, 0)]

    def test_get_cards_status_4_filter(self, mock_lingq_server):
        """Test status 4 filtering (status=3 AND extended_status=3)."""
        # Test data should have some cards with status=3 and extended_status=3
        # if not, it's better that the test fails
        response = requests.get("https://www.lingq.com/api/v3/es/cards/?status=4")
        assert response.status_code == 200

        data = response.json()
        assert len(data["results"]) > 0

        for card in data["results"]:
            assert card["status"] == 3
            assert card["extended_status"] == 3

    def test_patch_card(self, mock_lingq_server):
        all_cards = mock_lingq_server.get_all_cards("es")

        test_card = all_cards[0]
        new_status = (test_card["status"] + 1) % 4  # Cycle through statuses 0-3

        patch_response = requests.patch(
            f'https://www.lingq.com/api/v3/es/cards/{test_card["pk"]}/',
            data={"status": new_status, "extended_status": 0},
        )

        assert patch_response.status_code == 200

        updated_card = patch_response.json()
        assert updated_card["status"] == new_status
        assert updated_card["extended_status"] == 0
        assert updated_card["pk"] == test_card["pk"]

        card_from_db = mock_lingq_server.get_card_by_pk("es", test_card["pk"])
        assert card_from_db["status"] == new_status

    def test_patch_nonexistent_card(self, mock_lingq_server):
        response = requests.patch(
            "https://www.lingq.com/api/v3/es/cards/999999999/", data={"status": 1}
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestLingqApiIntegration:
    def test_get_lingqs_basic(self, mock_lingq_server):
        api = LingqApi("test_api_key", "es")
        lingqs = api.get_lingqs(include_knowns=True)

        assert len(lingqs) > 0

        for lingq in lingqs:
            assert isinstance(lingq, Lingq)
            assert hasattr(lingq, "primary_key")
            assert hasattr(lingq, "word")
            assert hasattr(lingq, "translations")
            assert hasattr(lingq, "status")

    def test_sync_statuses_to_lingq(self, mock_lingq_server):
        api = LingqApi("test_api_key", "es")

        # Get a real card from our mock data
        all_cards = api.get_lingqs(include_knowns=True)
        test_card = all_cards[0]
        new_status = (test_card.status + 1) % 4  # Cycle through statuses 0-3
        assert test_card.status != new_status

        test_lingq = Lingq(
            primary_key=test_card.primary_key,
            word=test_card.word,
            translations=test_card.translations,
            status=new_status,
            extended_status=0,
            tags=test_card.tags,
            fragment=test_card.fragment,
            importance=test_card.importance,
        )

        api.sync_statuses_to_lingq([test_lingq])

        updated_card = mock_lingq_server.get_card_by_pk("es", test_card.primary_key)
        assert updated_card["status"] == new_status
        assert updated_card["extended_status"] == 0


class TestLingqApiRateLimiting:
    def test_rate_limit_get_cards(self, mock_lingq_server):
        retry_delay_seconds = 2
        mock_lingq_server.enable_rate_limiting(retry_delay_seconds=retry_delay_seconds)
        api = LingqApi("test_api_key", "es")

        current_time = time.time()
        lingqs = api.get_lingqs(include_knowns=False)
        end_time = time.time()

        # LingqApi.get_all_lings uses a page size of 200
        number_of_pages = math.ceil(len(lingqs) / 200)
        # number_of_pages-1 because the first page doesn't get rate limited
        assert end_time - current_time > (number_of_pages - 1) * retry_delay_seconds
        assert end_time - current_time > 1  # Ensure that it took at least 1 second

        mock_lingq_server.disable_rate_limiting()

    def test_rate_limit_patch(self, mock_lingq_server):
        api = LingqApi("test_api_key", "es")
        all_cards = api.get_lingqs(include_knowns=False)
        test_card_data1 = all_cards[0]
        test_card_data2 = all_cards[1]

        retry_delay_seconds = 2
        mock_lingq_server.enable_rate_limiting(retry_delay_seconds=retry_delay_seconds)

        test_lingq1 = Lingq(
            primary_key=test_card_data1.primary_key,
            word=test_card_data1.word,
            translations=test_card_data1.translations,
            status=(test_card_data1.status + 1) % 4,
            extended_status=0,
            tags=test_card_data1.tags,
            fragment=test_card_data1.fragment,
            importance=test_card_data1.importance,
        )

        test_lingq2 = Lingq(
            primary_key=test_card_data2.primary_key,
            word=test_card_data2.word,
            translations=test_card_data2.translations,
            status=(test_card_data2.status + 1) % 4,
            extended_status=0,
            tags=test_card_data2.tags,
            fragment=test_card_data2.fragment,
            importance=test_card_data2.importance,
        )

        current_time = time.time()
        # First PATCH succeeds (establishes checkpoint)
        api.sync_statuses_to_lingq([test_lingq1])
        # Second PATCH should be rate limited and take time due to retry
        api.sync_statuses_to_lingq([test_lingq2])
        end_time = time.time()

        assert end_time - current_time > retry_delay_seconds
        assert end_time - current_time > 1  # Ensure that it took at least 1 second

        mock_lingq_server.disable_rate_limiting()
