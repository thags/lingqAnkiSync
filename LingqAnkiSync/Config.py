from Models.Lingq import Lingq
from typing import Dict

# fmt: off
lingq_langcodes = [
    'ar','hk','ca','zh','cs','da','nl','fi','el','he','id','it','ja','ko','la','no','fa','pl','pt',
    'ro','ru','sv','tr','uk','af','hy','be','bg','eo','ka','gu','hi','hu','is','km','mk','ms','pa',
    'sk','sl','sw','tl','vi', 'en', 'fr', 'de', 'es'
]
# fmt: on


class Config:
    def __init__(self, addon_manager):
        self.addon_manager = addon_manager
        self.config = self.addon_manager.getConfig(__name__)

    def _get_config(self, field_name: str) -> str:
        value = self.config[field_name]
        return "" if value is None or value == "" else str(value)

    def _set_config(self, field_name: str, set_to: str):
        self.config[field_name] = set_to
        self.addon_manager.writeConfig(__name__, self.config)

    def get_api_key(self):
        return self._get_config("apiKey")

    def set_api_key(self, set_to: str):
        self._set_config("apiKey", set_to)

    def get_language_code(self):
        return self._get_config("languageCode")

    def set_language_code(self, set_to: str):
        self._set_config("languageCode", set_to)

    def get_status_to_interval(self) -> Dict[str, int]:
        # Using a default anki ease factor of 2.5, this should make it so
        # that you need to complete two reviews of a card before it updates in
        # lingq with a higher known status
        #
        # e.g. card pulled from linq with status of 'recognized' (5 day review interval).
        # we see it and review it once correctly. card will still sync to lingq
        # as a status of 'recognized' until we see that card again in 32.5 days and review
        # correctly a second time.
        #
        # but also if we hit "easy" just once in anki then that will be sufficient
        # to increase the status to the next level
        return {
            Lingq.LEVEL_1: 0,
            Lingq.LEVEL_2: 5,
            Lingq.LEVEL_3: 13,
            Lingq.LEVEL_4: 34,
            Lingq.LEVEL_KNOWN: 85,
        }
