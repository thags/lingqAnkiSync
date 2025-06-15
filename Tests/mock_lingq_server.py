import json
import copy
import re
import urllib.parse
import time
import math
from typing import Dict, List, Tuple
from urllib.parse import urlparse, parse_qs, urlencode


class LingqApiRestServerMock:
    """
    A mock for the LingQ REST API that uses requests-mock to intercept HTTP calls.
    Uses lingq_data.json as the data source and maintains an in-memory database.

    Supports rate limiting simulation to test 429 handling.
    """

    def __init__(self, lingq_data: Dict[str, List[Dict]], requests_mock):
        self.requests_mock = requests_mock
        self._database = self.prep_database(lingq_data)

        # Rate limiting configuration - disabled by default
        self.retry_delay_seconds = 0  # 0 = no rate limiting, >0 = minimum seconds between requests
        self._last_request_time = None  # Timestamp of the last successful request

        # Matches {language_code}/cards or {language_code}/cards/{pk} (plus query params)
        self.get_url_regex = r"https://www\.lingq\.com/api/v3/(\w+)/cards/?(\d+)?"
        self.default_page = 1
        self.default_page_size = 50

        self._register_endpoints()

    def prep_database(self, db: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        lingq_db = copy.deepcopy(db)

        # Sorting the database simplifies pagination
        for key, lingqs in lingq_db.items():
            lingq_db[key] = sorted(lingqs, key=lambda x: x["pk"])

        return lingq_db

    def _register_endpoints(self):
        self.requests_mock.get(re.compile(self.get_url_regex), json=self._handle_get_cards)
        self.requests_mock.patch(re.compile(self.get_url_regex), json=self._handle_patch_card)

    def _check_rate_limit(self, context):
        """Check if request should be rate limited and return 429 if so."""
        if self.retry_delay_seconds == 0:
            return False

        current_time = time.time()
        if self._last_request_time is None:
            self._last_request_time = current_time
            return False

        # Check if enough time has elapsed since last request
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.retry_delay_seconds:
            # Calculate how much longer to wait
            retry_after = max(1, math.ceil(self.retry_delay_seconds - time_since_last))

            context.status_code = 429
            context.headers["Retry-After"] = str(retry_after)
            return True

        self._last_request_time = current_time
        return False

    def _extract_url_values(self, url: str) -> Tuple[str, int]:
        match = re.match(self.get_url_regex, url)
        language_code = match.group(1)
        primary_key = int(match.group(2)) if match.group(2) else None
        return language_code, primary_key

    def _extract_query_params(self, qs: Dict) -> Dict:
        page = int(qs["page"][0]) if "page" in qs else self.default_page
        page_size = int(qs["page_size"][0]) if "page_size" in qs else self.default_page_size
        # List of tuples of (status, extended_status)
        statuses = {(0, 0), (1, 0), (2, 0), (3, 0)}

        if "status" in qs:
            statuses = statuses & set([(int(s), 0) for s in qs["status"]])

            if "4" in qs["status"]:
                statuses.add((3, 3))

        return page, page_size, list(statuses)

    def _handle_get_cards(self, request, context):
        if self._check_rate_limit(context):
            return {"error": "Rate limit exceeded"}

        language_code, primary_key = self._extract_url_values(request.url)

        if language_code not in self._database.keys():
            context.status_code = 404
            return {"error": f"Language {language_code} not found"}

        # If primary_key is provided, return single card
        if primary_key:
            return self._handle_get_single_card(context, language_code, primary_key)

        # Handle collection request
        page, page_size, statuses = self._extract_query_params(request.qs)

        all_cards = self._database[language_code]
        filtered_cards = self._apply_status_filter(all_cards, statuses)

        # Pagination
        total_count = len(filtered_cards)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_cards = filtered_cards[start_idx:end_idx]

        response = {
            "count": total_count,
            "next": (
                request.url.replace(f"page={page}", f"page={page + 1}")
                if end_idx < total_count
                else None
            ),
            "previous": (
                request.url.replace(f"page={page}", f"page={page - 1}") if page > 1 else None
            ),
            "results": paginated_cards,
        }

        context.status_code = 200
        return response

    def _handle_get_single_card(self, context, language_code, primary_key):
        for card in self._database[language_code]:
            if card["pk"] == primary_key:
                context.status_code = 200
                return card

        context.status_code = 404
        return {"error": f"Card with pk {primary_key} not found"}

    def _apply_status_filter(self, cards: List[Dict], statuses: Dict) -> List[Dict]:
        filtered_cards = []
        for card in cards:
            if (card["status"], card["extended_status"]) in statuses:
                filtered_cards.append(card)

        return filtered_cards

    def _handle_patch_card(self, request, context):
        # Check rate limiting first
        if self._check_rate_limit(context):
            return {"error": "Rate limit exceeded"}

        language_code, primary_key = self._extract_url_values(request.url)

        if language_code not in self._database:
            context.status_code = 404
            return {"error": f"Language {language_code} not found"}

        if not primary_key:
            context.status_code = 400
            return {"error": "Primary key is required for PATCH requests"}

        card_index = None
        for i, card in enumerate(self._database[language_code]):
            if card.get("pk") == primary_key:
                card_index = i
                break

        if card_index is None:
            context.status_code = 404
            return {"error": f"Card with pk {primary_key} not found"}

        update_data = self._parse_request_data(request)
        if not update_data:
            context.status_code = 400
            return {"error": "No data provided for update"}

        for key in ["status", "extended_status"]:
            if key in update_data:
                self._database[language_code][card_index][key] = update_data[key]

        context.status_code = 200
        return self._database[language_code][card_index]

    def _parse_request_data(self, request) -> Dict:
        """Parse form data from request body."""
        body_str = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
        update_data = dict(urllib.parse.parse_qsl(body_str))

        for key in ["status", "extended_status"]:
            if key in update_data:
                update_data[key] = int(update_data[key])

        return update_data

    # ============================================================================
    # Test Helper Methods
    # ============================================================================
    def get_card_by_pk(self, language_code: str, primary_key: int) -> Dict:
        for card in self._database[language_code]:
            if card["pk"] == primary_key:
                return card

    def get_all_cards(self, language_code: str) -> List[Dict]:
        return self._database.get(language_code, [])

    def find_card_by_status(
        self, language_code: str, status: int, extended_status: int = 0
    ) -> Dict:
        """Find the first card with the specified status."""
        for card in self._database.get(language_code, []):
            if card["status"] == status and card["extended_status"] == extended_status:
                return card
        return None

    # ============================================================================
    # Rate Limiting Test Helper Methods
    # ============================================================================
    def reset_rate_limit(self):
        self._last_request_time = None

    def enable_rate_limiting(self, retry_delay_seconds: int):
        self.retry_delay_seconds = retry_delay_seconds

    def disable_rate_limiting(self):
        self.retry_delay_seconds = 0
        self._last_request_time = None
