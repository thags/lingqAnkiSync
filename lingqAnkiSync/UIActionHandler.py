from .Converter import anki_cards_to_lingqs, lingqs_to_anki_cards
from .LingqApi import LingqApi
from .Config import Config, lingq_langcodes
from .Models.Lingq import Lingq
from .Models.AnkiCard import AnkiCard
from typing import List, Dict, Tuple
from . import AnkiHandler


class ActionHandler:
    def __init__(self, addon_manager):
        self.config = Config(addon_manager)

    def import_lingqs_to_anki(self, deck_name: str, import_knowns: bool) -> int:
        api_key = self.config.get_api_key()
        language_code = self.config.get_language_code()
        status_to_interval = self.config.get_status_to_interval()

        self._check_language_code(language_code)

        lingqs = LingqApi(api_key, language_code).get_lingqs(import_knowns)
        cards = lingqs_to_anki_cards(lingqs, status_to_interval)
        return AnkiHandler.create_notes_from_cards(cards, deck_name)

    def sync_lingq_status_to_lingq(
        self, deck_name: str, downgrade: bool = False, progress_callback=None
    ) -> Tuple[int, int, int]:
        api_key = self.config.get_api_key()
        language_code = self.config.get_language_code()
        status_to_interval = self.config.get_status_to_interval()

        self._check_language_code(language_code)

        cards = AnkiHandler.get_all_cards_in_deck(deck_name)
        cards_to_increase, cards_to_decrease = self._prep_cards_for_update(
            cards, status_to_interval, downgrade
        )
        cards_to_update = cards_to_increase + cards_to_decrease

        lingqs = anki_cards_to_lingqs(cards_to_update, status_to_interval)
        successful_updates = LingqApi(api_key, language_code).sync_statuses_to_lingq(
            lingqs, progress_callback
        )
        self._update_notes_in_anki(deck_name, cards_to_update)

        return len(cards_to_increase), len(cards_to_decrease), successful_updates

    def _check_language_code(self, language_code: str):
        if language_code and language_code not in lingq_langcodes:
            raise ValueError(
                f'Language code "{language_code}" is not valid. Examples include "es", "de", "ja", etc.'
            )

    def _prep_cards_for_update(
        self, anki_cards: List[AnkiCard], status_to_interval: Dict[str, int], downgrade: bool
    ) -> Tuple[List[AnkiCard], List[AnkiCard]]:
        """pre-checking if cards should update, to limit API calls later on
        and prepping card for update in anki db

        :returns two lists of cards that need to be updated in LingQ
        """
        cards_to_increase = []
        cards_to_decrease = []

        for card in anki_cards:
            next_level = Lingq.get_next_level(card.status)
            prev_level = Lingq.get_prev_level(card.status)
            if next_level is not None and (card.interval > status_to_interval[next_level]):
                card.status = next_level
                cards_to_increase.append(card)

            if (
                downgrade
                and prev_level is not None
                and card.interval < status_to_interval[card.status]
            ):
                card.status = prev_level
                cards_to_decrease.append(card)

        return cards_to_increase, cards_to_decrease

    def _update_notes_in_anki(self, deck_name: str, cards: List[AnkiCard]):
        for card in cards:
            AnkiHandler.update_card_status(deck_name, card.primary_key, card.status)

    def set_configs(self, api_key, language_code):
        self.config.set_api_key(api_key)
        self.config.set_language_code(language_code)

    def get_deck_names(self) -> List:
        return AnkiHandler.get_all_deck_names()

    def get_api_key(self) -> str:
        return self.config.get_api_key()

    def get_language_code(self) -> str:
        return self.config.get_language_code()
