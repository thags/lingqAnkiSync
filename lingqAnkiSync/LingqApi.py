import requests
import time
from typing import List, NoReturn
from .Models.Lingq import Lingq
from . import Converter


class LingqApi:
    def __init__(self, api_key: str, language_code: str):
        self.api_key = api_key
        self.language_code = language_code
        self._baseUrl = f"https://www.lingq.com/api/v3/{language_code}/cards"
        self.unformatted_lingqs = []
        self.lingqs = []

    def get_lingqs(self, include_knowns: bool) -> List[Lingq]:
        next_url = self._baseUrl + "?page=1&page_size=200"

        while next_url is not None:
            if not include_knowns:
                next_url += "&status=0&status=1&status=2&status=3"

            words_response = self._get_single_page(next_url)
            words = words_response.json()["results"]
            self.unformatted_lingqs.extend(words)
            next_url = words_response.json()["next"]
            time.sleep(2)

        self._convert_api_to_lingqs()
        return self.lingqs

    def with_retry(self, requests_func, **kwargs):
        try:
            response = requests_func(**kwargs)
            response.raise_for_status()
        except Exception as e:
            if response.status_code == 429:
                sleep_time = int(response.headers["Retry-After"]) + 3 # A little buffer
                time.sleep(sleep_time)
                try:
                    response = requests_func(**kwargs)
                    response.raise_for_status()
                except:
                    raise TypeError(
                        f'sleep time: {sleep_time} still not enough. {response.status_code} {response.headers["Retry-After"]}')
            else:
                raise e

        # TODO is there a bug where when an exception happens, this is returned as null instead of the exception being caught?
        # TODO test this out with wifi turned off and see what happens
        return response

    def _get_single_page(self, url):
        headers = {"Authorization": f"Token {self.api_key}"}
        words_response = self.with_retry(requests.get, url=url, headers=headers)

        return words_response

    def _convert_api_to_lingqs(self) -> NoReturn:
        for lingq in self.unformatted_lingqs:
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

    def sync_statuses_to_lingq(self, lingqs: List[Lingq]):
        for lingq in lingqs:
            if self._should_update(lingq):
                headers = {"Authorization": f"Token {self.api_key}"}
                url = f"{self._baseUrl}/{lingq.primary_key}/"
                data = {"status": lingq.status, "extended_status": lingq.extended_status}

                self.with_retry(requests.patch, url=url, headers=headers, data=data)

    def _get_lingq_status(self, lingq_pk):
        url = f"{self._baseUrl}/{lingq_pk}/"
        response = self._get_single_page(url)
        internal_status = response.json()["status"]
        extended_status = response.json()["extended_status"]

        return Converter.lingq_internal_status_to_status(internal_status, extended_status)

    def _should_update(self, lingq) -> bool:
        current_card_status = Converter.lingq_internal_status_to_status(
            lingq.status, lingq.extended_status
        )
        lingq_api_status = self._get_lingq_status(lingq.primary_key)
        return lingq_api_status != current_card_status
