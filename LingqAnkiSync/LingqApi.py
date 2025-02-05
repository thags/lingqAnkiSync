import math
import requests
import time
from typing import List
from Models.Lingq import Lingq
from concurrent.futures import ThreadPoolExecutor, as_completed

class LingqApi:
    def __init__(self, apiKey: str, languageCode: str, import_knowns: bool):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self.import_knowns = import_knowns
        self._baseUrl = f"https://www.lingq.com/api/v3/{languageCode}/cards"
        self.unformatedLingqs = []
        self.lingqs = []

    def GetLingqs(self) -> List[Lingq]:
        page = 1

        firstPageUrl = f"{self._baseUrl}?page=1&page_size=200"
        pageResult = self._GetSinglePage(firstPageUrl)
        self.unformatedLingqs.extend(pageResult.json()['results'])
        totalPages = math.ceil(pageResult.json()['count'] / 200)
        page += 1

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            while totalPages >= page:
                nextUrl = f"{self._baseUrl}?page={page}&page_size=200"
                if not self.import_knowns:
                    nextUrl += '&status=0&status=1&status=2&status=3'
        
                url_future = executor.submit(self._GetSinglePage, nextUrl)
                futures.append(url_future)
                page += 1

            for future in as_completed(futures):
                try:
                    result = future.result()
                    words = result.json()['results']
                    self.unformatedLingqs.extend(words)
                except requests.exceptions.RequestException as e:
                    continue

        # this could also be handled in parralel
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
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
        for lingq in lingqs:
            if (self._ShouldUpdateStatus(lingq.primaryKey, lingq.status) == False): continue
            lingq_future = executor.submit(self._GetLingqStatusReadyForSync, lingq)
            url_future = executor.submit(
                self._PatchLingqStatusToLingq,
                lingq_future.result(),
                f"{self._baseUrl}/{lingq.primaryKey}/",
                {"status": lingq.status, "extended_status": lingq.extended_status})
            futures.append(url_future)

            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except requests.exceptions.RequestException as e:
                    continue
            return len(results)

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
