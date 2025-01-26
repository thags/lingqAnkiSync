from .Converter import anki_cards_to_lingqs, lingqs_to_anki_cards
from .AnkiHandler import create_notes_from_cards, get_all_cards_in_deck, get_all_deck_names
from .LingqApi import LingqApi
from .Config import Config, lingq_langcodes
from .Models.Lingq import Lingq
from .Models.AnkiCard import AnkiCard
from typing import List, Dict


class ActionHandler:
    def __init__(self, addon_manager):
        self.config = Config(addon_manager)

    def import_lingqs_to_anki(self, deck_name: str, import_knowns: bool) -> int:
        api_key = self.get_api_key()
        language_code = self.get_language_code()
        status_to_interval = self.config.get_status_to_interval()

        self._check_language_code(language_code)

        lingqs = LingqApi(api_key, language_code, import_knowns).get_lingqs()
        cards = lingqs_to_anki_cards(lingqs, status_to_interval)
        return create_notes_from_cards(cards, deck_name)

    def sync_lingq_status_to_lingq(self, deck_name: str) -> int:
        api_key = self.config.get_api_key()
        language_code = self.config.get_language_code()
        status_to_interval = self.config.get_status_to_interval()

        self._check_language_code(language_code)

        cards = get_all_cards_in_deck(deck_name)
        # pre-checking if cards should update, to limit API calls later on
        cards_to_update = self._find_cards_to_update(cards, status_to_interval)
        lingqs = anki_cards_to_lingqs(cards_to_update, status_to_interval)

        return LingqApi(api_key, language_code).sync_statuses_to_lingq(lingqs)

    def _check_language_code(self, language_code):
        if language_code and language_code not in lingq_langcodes:
            raise ValueError(
                f'Language code "{language_code}" is not valid. Examples include "es", "de", "ja", etc.'
            )

    def _find_cards_to_update(self, anki_cards: List[AnkiCard], status_to_interval: Dict[str, int]):
        cards_to_update = []

        for card in anki_cards:
            if card.status != Lingq.LEVEL_KNOWN:
                next_level = Lingq.LEVELS[Lingq.LEVELS.index(card.status) + 1]
                next_level_interval = status_to_interval[next_level]

                if card.interval > next_level_interval:
                    cards_to_update.append(card)

        return cards_to_update

    def set_configs(self, api_key, language_code):
        self.config.set_api_key(api_key)
        self.config.set_language_code(language_code)

    def get_deck_names(self) -> List:
        return get_all_deck_names()

    def get_api_key(self) -> str:
        return self.config.get_api_key()

    def get_language_code(self) -> str:
        return self.config.get_language_code()
