import requests
import time
from typing import List
from Models.Lingq import Lingq
import Converter


class LingqApi:
    def __init__(self, apiKey: str, languageCode: str, import_knowns: bool):
        self.api_key = apiKey
        self.language_code = languageCode
        self.import_knowns = import_knowns
        self._baseUrl = f"https://www.lingq.com/api/v3/{languageCode}/cards"
        self.unformated_lingqs = []
        self.lingqs = []

    def get_lingqs(self) -> List[Lingq]:
        next_url = self._baseUrl + "?page=1&page_size=200"

        while next_url != None:
            if not self.import_knowns:
                next_url += "&status=0&status=1&status=2&status=3"

            words_response = self._get_single_page(next_url)
            words = words_response.json()["results"]
            self.unformated_lingqs.extend(words)
            next_url = words_response.json()["next"]
            time.sleep(2)

        self._convert_api_to_lingqs()
        return self.lingqs

    def _get_single_page(self, url):
        headers = {"Authorization": f"Token {self.api_key}"}
        words_response = requests.get(url, headers=headers)
        words_response.raise_for_status()
        return words_response

    def _convert_api_to_lingqs(self) -> List[Lingq]:
        for lingq in self.unformated_lingqs:
            translations = [hint["text"] for hint in lingq["hints"]]
            popularity = max((hint["popularity"] for hint in lingq["hints"]), default=0)
            if len(translations) > 0:
                self.lingqs.append(
                    Lingq(
                        lingq["pk"],
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

    def sync_statuses_to_lingq(self, lingqs: List[Lingq]) -> int:
        lingqs_updated = 0

        for lingq in lingqs:
            if self._should_update(lingq):
                headers = {"Authorization": f"Token {self.api_key}"}
                url = f"{self._baseUrl}/{lingq.primary_key}/"
                response = requests.patch(
                    url,
                    headers=headers,
                    data={"status": lingq.status, "extended_status": lingq.extended_status},
                )
                response.raise_for_status()
                lingqs_updated += 1

        return lingqs_updated

    def _get_lingq_status(self, lingq_pk):
        url = f"{self._baseUrl}/{lingq_pk}/"
        response = self._get_single_page(url)
        internal_status = response.json()["status"]
        extended_status = response.json()["extended_status"]

        return Converter.lingq_internal_status_to_status(internal_status, extended_status)

    def _should_update(self, lingq) -> bool:
        new_status = Converter.lingq_internal_status_to_status(lingq.status, lingq.extended_status)
        lingq_current_status = self._get_lingq_status(lingq.primary_key)
        return Lingq.LEVELS.index(lingq_current_status) < Lingq.LEVELS.index(new_status)
