import requests
import time
from typing import List, NoReturn, Callable, Optional
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
        next_url = f"{self._baseUrl}?page=1&page_size=200"
        if not include_knowns:
            next_url += "&status=0&status=1&status=2&status=3"

        while next_url is not None:
            words_response = self._get_single_page(next_url)
            words = words_response.json()["results"]
            self.unformatted_lingqs.extend(words)
            next_url = words_response.json()["next"]

        self._convert_api_to_lingqs()
        return self.lingqs

    def with_retry(self, requests_func, **kwargs):
        """
        Execute a request with retry logic for 429 responses

        Args:
            requests_func: The requests function to call (requests.get, requests.patch, etc.)
            **kwargs: Arguments to pass to the requests function
        """
        try:
            response = None
            response = requests_func(**kwargs)
            response.raise_for_status()
        except Exception as e:
            if response is not None and response.status_code == 429:
                sleep_time = int(response.headers["Retry-After"]) + 3  # A little buffer

                if hasattr(self, "rate_limit_callback") and self.rate_limit_callback:
                    for seconds_remaining in range(sleep_time, 0, -1):
                        self.rate_limit_callback(seconds_remaining)
                        time.sleep(1)
                else:
                    time.sleep(sleep_time)

                # Retry the request
                response = requests_func(**kwargs)
                response.raise_for_status()
            else:
                raise e

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

    def sync_statuses_to_lingq(self, lingqs: List[Lingq], progress_callback=None) -> int:
        successful_updates = 0
        total_lingqs = len(lingqs)

        for i, lingq in enumerate(lingqs):
            # Create a wrapper callback for with_retry to pass to the rate limiting info
            self.rate_limit_callback = lambda seconds_remaining: (
                progress_callback(i, total_lingqs, lingq.word, seconds_remaining)
                if progress_callback
                else None
            )

            if self._should_update(lingq):
                headers = {"Authorization": f"Token {self.api_key}"}
                url = f"{self._baseUrl}/{lingq.primary_key}/"
                data = {"status": lingq.status, "extended_status": lingq.extended_status}

                self.with_retry(requests.patch, url=url, headers=headers, data=data)
                successful_updates += 1

            if progress_callback:
                progress_callback(i + 1, total_lingqs, lingq.word)

        del self.rate_limit_callback
        return successful_updates

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
