import requests
import time
from typing import List, Dict
from Models.Lingq import Lingq


class LingqApi:
    def __init__(self, apiKey: str, languageCode: str, import_knowns: bool = True):

        self.apiKey = apiKey
        self.languageCode = languageCode
        self.import_knowns = import_knowns
        self._baseUrl = f"https://www.lingq.com/api/v3/{languageCode}/cards"
        self.unformatedLingqs = []
        self.lingqs = []

        self.updatedLingqs = {}

    def GetLingqs(self, delay=2, return_dict=False) -> List[Lingq]:
        nextUrl = self._baseUrl + "?page=1&page_size=200"
        count = 0
        while (nextUrl != None):
            if not self.import_knowns:
                nextUrl += '&status=0&status=1&status=2&status=3'

            words_response = self._GetSinglePage(nextUrl)
            words = words_response.json()['results']
            count += len(words)
            self.unformatedLingqs.extend(words)
            nextUrl = words_response.json()['next']

            print(f"Downloaded {count} total lingqs. Waiting {delay} seconds before next request...")
            # Delay between requests to avoid rate limiting
            time.sleep(delay)
        print("Finished. Downloaded a total of {count} lingqs.")

        if return_dict:
            return self._ConvertApiToLingqsDict()
        else:
            return self._ConvertApiToLingqs()

    def _GetSinglePage(self, url):
        headers = {'Authorization': f'Token {self.apiKey}'}
        words_response = requests.get(url, headers=headers)
        words_response.raise_for_status()
        return words_response

    def _ConvertApiToLingqs(self) -> List[Lingq]:
        # I should remove this function and use _ConvertApiToLingqsDict for everything instead.
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
        return self.lingqs

    def _ConvertApiToLingqsDict(self) -> Dict[int, Lingq]:
        lingq_dict = {}
        for lingq in self.unformatedLingqs:
            translations = [hint['text'] for hint in lingq['hints']]
            popularity = max((hint['popularity'] for hint in lingq['hints']), default=0)
            if translations:
                lingq_obj = Lingq(
                    lingq['pk'],
                    lingq['term'],
                    translations,
                    lingq['status'],
                    lingq['extended_status'],
                    lingq['tags'],
                    lingq['fragment'],
                    lingq['importance'],
                    popularity
                )
                lingq_dict[str(lingq['pk'])] = lingq_obj
        return lingq_dict


    def SyncStatusesToLingq(self, lingqs: List[Lingq]) -> int:
        self._GetMostRecentLingqStatus()
        delay = 1.0  # initial delay in seconds
        lingqsUpdated = 0
        lingqsIgnored = 0
        for i, lingq in enumerate(lingqs):
            print(f"{i+1}/{len(lingqs)} - Checking: {lingq.word} ...", end=" ")

            if (self._ShouldUpdateStatus(lingq.primaryKey, lingq.status) == False):
                print("Skipped. Already up to date.")
                lingqsIgnored += 1
                continue

            lingq = self._GetLingqStatusReadyForSync(lingq)
            headers = {"Authorization": f"Token {self.apiKey}"}
            url = f"{self._baseUrl}/{lingq.primaryKey}/"
            response = requests.patch(url, headers=headers, data={
                            "status": lingq.status,
                            "extended_status": lingq.extended_status})
            response.raise_for_status()
            print("Uploaded.")
            time.sleep(delay)        
            lingqsUpdated += 1

        print(f"Finished. Updated a total of {lingqsUpdated} lingqs. Ignored {lingqsIgnored} lingqs.")
        return lingqsUpdated

    def _GetLingqStatusOLD(self, lingqPrimaryKey):
        url = f"{self._baseUrl}/{lingqPrimaryKey}/"
        response = self._GetSinglePage(url)
        status = response.json()['status']
        extendedStatus = response.json()['extended_status']
        if (extendedStatus == 3 and status == 3):
            status = 4
        if (extendedStatus == 0 and status == 3):
            status = 2
        return status
    
    def _GetMostRecentLingqStatus(self):
        self.updatedLingqs = LingqApi(self.apiKey, self.languageCode, self.import_knowns).GetLingqs(delay=10, return_dict=True)
    
    def _GetLingqStatus(self, lingqPrimaryKey):

        if lingqPrimaryKey not in self.updatedLingqs:
            print("Lingq not found in downloaded data. Did you remove it from the LingQ site?")
            print("Ignored.")
            return 0

        status = self.updatedLingqs[lingqPrimaryKey].status
        extendedStatus = self.updatedLingqs[lingqPrimaryKey].extended_status

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
