import requests
import time
from typing import List
from Models.Lingq import Lingq
import Converter

class LingqApi:
    def __init__(self, apiKey, languageCode):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self._baseUrl = f"https://www.lingq.com/api/v3/{languageCode}/cards"
        self.unformatedLingqs = []
        self.lingqs = []

    def GetAllLingqs(self) -> List[Lingq]:
        nextUrl = self._baseUrl + "?page=1&page_size=200"
        while (nextUrl != None):
            words_response = self._GetSinglePage(nextUrl)
            words = words_response.json()['results']
            self.unformatedLingqs.extend(words)
            nextUrl = words_response.json()['next']
            time.sleep(2)
        self._ConvertApiToLingqs()
        return self.lingqs

    def _GetSinglePage(self, url):
        headers = {'Authorization': f'Token {self.apiKey}'}
        words_response = requests.get(url, headers=headers)
        words_response.raise_for_status()
        return words_response

    def _ConvertApiToLingqs(self) -> List[Lingq]:
        for lingq in self.unformatedLingqs:
            translations = [hint['text'] for hint in lingq['hints']]
            popularity = max((hint['popularity'] for hint in lingq['hints']), default=0)
            if len(translations) > 0:
                self.lingqs.append(
                    Lingq(
                        lingq['pk'],
                        lingq['term'],
                        translations,
                        lingq['status'],
                        lingq['extended_status'],
                        lingq['tags'],
                        lingq['fragment'],
                        lingq['importance'],
                        popularity
                    ))

    def SyncStatusesToLingq(self, lingqs: List[Lingq]) -> int:
        lingqsUpdated = 0

        for lingq in lingqs:
            if self._ShouldUpdate(lingq):
                headers = {"Authorization": f"Token {self.apiKey}"}
                url = f"{self._baseUrl}/{lingq.primaryKey}/"
                response = requests.patch(url, headers=headers, data={
                    "status": lingq.status, "extended_status": lingq.extended_status})
                response.raise_for_status()
                lingqsUpdated += 1

        return lingqsUpdated

    def _GetLingqStatus(self, lingq_primary_key):
        url = f"{self._baseUrl}/{lingq_primary_key}/"
        response = self._GetSinglePage(url)
        internal_status = response.json()['status']
        extended_status = response.json()['extended_status']

        return Converter._LingqInternalStatusToStatus(internal_status, extended_status)

    def _ShouldUpdate(self, lingq) -> bool:
        newStatus = Converter._LingqInternalStatusToStatus(lingq.status, lingq.extended_status)
        lingqCurrentStatus = self._GetLingqStatus(lingq.primaryKey)
        return Lingq.LEVELS.index(lingqCurrentStatus) < Lingq.LEVELS.index(newStatus)
