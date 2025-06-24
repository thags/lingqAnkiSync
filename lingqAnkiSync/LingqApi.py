import requests
import time
from typing import List, NoReturn, Callable, Optional
from .Models.Lingq import Lingq
from . import Converter


class LingqApi:
    def __init__(self, apiKey: str, languageCode: str):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self._baseUrl = f"https://www.lingq.com/api/v3/{languageCode}/cards"
        self.unformattedLingqs = []
        self.lingqs = []

    def GetLingqs(self, includeKnowns: bool) -> List[Lingq]:
        nextUrl = f"{self._baseUrl}?page=1&page_size=200"
        if not includeKnowns:
            nextUrl += "&status=0&status=1&status=2&status=3"

        while nextUrl is not None:
            wordsResponse = self._GetSinglePage(nextUrl)
            words = wordsResponse.json()["results"]
            self.unformattedLingqs.extend(words)
            nextUrl = wordsResponse.json()["next"]

        self._ConvertApiToLingqs()
        return self.lingqs

    def WithRetry(self, requestsFunc, **kwargs):
        """
        Execute a request with retry logic for 429 responses

        Args:
            requestsFunc: The requests function to call (requests.get, requests.patch, etc.)
            **kwargs: Arguments to pass to the requests function
        """
        try:
            response = None
            response = requestsFunc(**kwargs)
            response.raise_for_status()
        except Exception as e:
            if response is not None and response.status_code == 429:
                sleepTime = int(response.headers["Retry-After"]) + 3  # A little buffer

                if hasattr(self, "rateLimitCallback") and self.rateLimitCallback:
                    for secondsRemaining in range(sleepTime, 0, -1):
                        self.rateLimitCallback(secondsRemaining)
                        time.sleep(1)
                else:
                    time.sleep(sleepTime)

                # Retry the request
                response = requestsFunc(**kwargs)
                response.raise_for_status()
            else:
                raise e

        return response

    def _GetSinglePage(self, url):
        headers = {"Authorization": f"Token {self.apiKey}"}
        wordsResponse = self.WithRetry(requests.get, url=url, headers=headers)

        return wordsResponse

    def _ConvertApiToLingqs(self) -> NoReturn:
        for lingq in self.unformattedLingqs:
            translations = [hint["text"] for hint in lingq["hints"]]
            popularity = max((hint["popularity"] for hint in lingq["hints"]), default=0)
            if len(translations) > 0:
                self.lingqs.append(
                    Lingq(
                        int(lingq["pk"]),
                        lingq["term"],
                        translations,
                        lingq["status"],
                        lingq["extended_status"],
                        lingq["tags"],
                        lingq["fragment"],
                        lingq["importance"],
                        popularity,
                    )
                )

    def SyncStatusesToLingq(self, lingqs: List[Lingq], progressCallback=None) -> int:
        successfulUpdates = 0
        totalLingqs = len(lingqs)

        for i, lingq in enumerate(lingqs):
            # Create a wrapper callback for WithRetry to pass to the rate limiting info
            self.rateLimitCallback = lambda secondsRemaining: (
                progressCallback(i, totalLingqs, lingq.word, secondsRemaining)
                if progressCallback
                else None
            )

            if self._ShouldUpdate(lingq):
                headers = {"Authorization": f"Token {self.apiKey}"}
                url = f"{self._baseUrl}/{lingq.primaryKey}/"
                data = {"status": lingq.status, "extended_status": lingq.extendedStatus}

                self.WithRetry(requests.patch, url=url, headers=headers, data=data)
                successfulUpdates += 1

            if progressCallback:
                progressCallback(i + 1, totalLingqs, lingq.word)

        del self.rateLimitCallback
        return successfulUpdates

    def _GetLingqStatus(self, lingqPk):
        url = f"{self._baseUrl}/{lingqPk}/"
        response = self._GetSinglePage(url)
        internalStatus = response.json()["status"]
        extendedStatus = response.json()["extended_status"]

        return Converter.LingqInternalStatusToStatus(internalStatus, extendedStatus)

    def _ShouldUpdate(self, lingq) -> bool:
        currentCardStatus = Converter.LingqInternalStatusToStatus(
            lingq.status, lingq.extendedStatus
        )
        lingqApiStatus = self._GetLingqStatus(lingq.primaryKey)
        return lingqApiStatus != currentCardStatus
