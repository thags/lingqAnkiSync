import requests
import time
from typing import List
from Models.Lingq import Lingq

class LingqApi:
    def __init__(self, apiKey: str, languageCode: str, import_knowns: bool):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self.import_knowns = import_knowns
        self._baseUrl = f"https://www.lingq.com/api/v3/{languageCode}/cards"
        self.unformatedLingqs = []
        self.lingqs = []

    def GetLingqs(self) -> List[Lingq]:
        nextUrl = self._baseUrl + "?page=1&page_size=200"

        while (nextUrl != None):
            if not self.import_knowns:
                nextUrl += '&status=0&status=1&status=2&status=3'

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
            if (self._ShouldUpdateStatus(lingq.primaryKey, lingq.status) == False): continue
            lingq = self._GetLingqStatusReadyForSync(lingq)
            headers = {"Authorization": f"Token {self.apiKey}"}
            url = f"{self._baseUrl}/{lingq.primaryKey}/"
            response = requests.patch(url, headers=headers, data={
                "status": lingq.status, "extended_status": lingq.extended_status})
            response.raise_for_status()
            lingqsUpdated += 1
        return lingqsUpdated

    def _GetLingqStatus(self, lingqPrimaryKey):
        url = f"{self._baseUrl}/{lingqPrimaryKey}/"
        response = self._GetSinglePage(url)
        status = response.json()['status']
        extendedStatus = response.json()['extended_status']
        if (extendedStatus == 3 and status == 3):
            status = 4
        if (extendedStatus == 0 and status == 3):
            status = 2
        return status

    def _GetLingqStatusReadyForSync(self, lingq: Lingq):
        if (lingq.status == 4):
            lingq.extended_status = 3
            lingq.status = 3
        else:
            lingq.extended_status = 0
        return lingq

    def _ShouldUpdateStatus(self, lingqPrimaryKey, newStatus) -> bool:
        lingqCurrentStatus = self._GetLingqStatus(lingqPrimaryKey)
        return int(lingqCurrentStatus) < int(newStatus)
