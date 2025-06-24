import pytest
import requests
import time
import math
from unittest.mock import patch
from LingqAnkiSync.LingqApi import LingqApi
from LingqAnkiSync.Models.Lingq import Lingq


class TestLingqApiMock:
    def test_get_cards_basic(self, mockLingqServer):
        response = requests.get("https://www.lingq.com/api/v3/es/cards/")
        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert "results" in data
        assert isinstance(data["results"], list)
        assert data["count"] > 0

    def test_get_cards_pagination(self, mockLingqServer):
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
            page1Pks = {card["pk"] for card in data1["results"]}
            page2Pks = {card["pk"] for card in data2["results"]}
            assert page1Pks.isdisjoint(page2Pks), "Pages should not contain overlapping cards"

    def test_get_cards_status_filter(self, mockLingqServer):
        # Get cards with status 0 (new)
        response = requests.get("https://www.lingq.com/api/v3/es/cards/?status=0&status=2")
        assert response.status_code == 200

        data = response.json()
        for card in data["results"]:
            assert (card["status"], card["extended_status"]) in [(0, 0), (2, 0)]

    def test_get_cards_status_4_filter(self, mockLingqServer):
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

    def test_patch_card(self, mockLingqServer):
        allCards = mockLingqServer.get_all_cards("es")

        testCard = allCards[0]
        newStatus = (testCard["status"] + 1) % 4  # Cycle through statuses 0-3

        patchResponse = requests.patch(
            f'https://www.lingq.com/api/v3/es/cards/{testCard["pk"]}/',
            data={"status": newStatus, "extended_status": 0},
        )

        assert patchResponse.status_code == 200

        updatedCard = patchResponse.json()
        assert updatedCard["status"] == newStatus
        assert updatedCard["extended_status"] == 0
        assert updatedCard["pk"] == testCard["pk"]

        cardFromDb = mockLingqServer.get_card_by_pk("es", testCard["pk"])
        assert cardFromDb["status"] == newStatus

    def test_patch_nonexistent_card(self, mockLingqServer):
        response = requests.patch(
            "https://www.lingq.com/api/v3/es/cards/999999999/", data={"status": 1}
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestLingqApiIntegration:
    def test_get_lingqs_basic(self, mockLingqServer):
        api = LingqApi("test_api_key", "es")
        lingqs = api.GetLingqs(includeKnowns=True)

        assert len(lingqs) > 0

        for lingq in lingqs:
            assert isinstance(lingq, Lingq)
            assert hasattr(lingq, "primaryKey")
            assert hasattr(lingq, "word")
            assert hasattr(lingq, "translations")
            assert hasattr(lingq, "status")

    def test_sync_statuses_to_lingq(self, mockLingqServer):
        api = LingqApi("test_api_key", "es")

        # Get a real card from our mock data
        allCards = api.GetLingqs(includeKnowns=True)
        testCard = allCards[0]
        newStatus = (testCard.status + 1) % 4  # Cycle through statuses 0-3
        assert testCard.status != newStatus

        testLingq = Lingq(
            primaryKey=testCard.primaryKey,
            word=testCard.word,
            translations=testCard.translations,
            status=newStatus,
            extendedStatus=0,
            tags=testCard.tags,
            fragment=testCard.fragment,
            importance=testCard.importance,
        )

        api.SyncStatusesToLingq([testLingq])

        updatedCard = mockLingqServer.get_card_by_pk("es", testCard.primaryKey)
        assert updatedCard["status"] == newStatus
        assert updatedCard["extended_status"] == 0


class TestLingqApiRateLimiting:
    def test_rate_limit_get_cards(self, mockLingqServer):
        retryDelaySeconds = 2
        mockLingqServer.enable_rate_limiting(retry_delay_seconds=retryDelaySeconds)
        api = LingqApi("test_api_key", "es")

        currentTime = time.time()
        lingqs = api.GetLingqs(includeKnowns=False)
        endTime = time.time()

        # LingqApi.GetLingqs uses a page size of 200
        numberOfPages = math.ceil(len(lingqs) / 200)
        # numberOfPages-1 because the first page doesn't get rate limited
        assert endTime - currentTime > (numberOfPages - 1) * retryDelaySeconds
        assert endTime - currentTime > 1  # Ensure that it took at least 1 second

        mockLingqServer.disable_rate_limiting()

    def test_rate_limit_patch(self, mockLingqServer):
        api = LingqApi("test_api_key", "es")
        allCards = api.GetLingqs(includeKnowns=False)
        testCardData1 = allCards[0]
        testCardData2 = allCards[1]

        retryDelaySeconds = 2
        mockLingqServer.enable_rate_limiting(retry_delay_seconds=retryDelaySeconds)

        testLingq1 = Lingq(
            primaryKey=testCardData1.primaryKey,
            word=testCardData1.word,
            translations=testCardData1.translations,
            status=(testCardData1.status + 1) % 4,
            extendedStatus=0,
            tags=testCardData1.tags,
            fragment=testCardData1.fragment,
            importance=testCardData1.importance,
        )

        testLingq2 = Lingq(
            primaryKey=testCardData2.primaryKey,
            word=testCardData2.word,
            translations=testCardData2.translations,
            status=(testCardData2.status + 1) % 4,
            extendedStatus=0,
            tags=testCardData2.tags,
            fragment=testCardData2.fragment,
            importance=testCardData2.importance,
        )

        currentTime = time.time()
        # First PATCH succeeds (establishes checkpoint)
        api.SyncStatusesToLingq([testLingq1])
        # Second PATCH should be rate limited and take time due to retry
        api.SyncStatusesToLingq([testLingq2])
        endTime = time.time()

        assert endTime - currentTime > retryDelaySeconds
        assert endTime - currentTime > 1  # Ensure that it took at least 1 second

        mockLingqServer.disable_rate_limiting()
