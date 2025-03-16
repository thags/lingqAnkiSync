# frozen_string_literal: true

import sys, os
sys.path.append(
    os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync")
)
from LingqApi import LingqApi

class TestLingqApi:
    def test_should_set_import_knowns_to_true_by_default(self):
        api = LingqApi("test_key", "test_lang")
        assert api.import_knowns == True

    def test_should_set_import_knowns_to_false_when_specified(self):
        api = LingqApi("test_key", "test_lang", import_knowns=False)
        assert api.import_knowns == False

    def test_should_set_import_knowns_to_true_when_specified(self):
        api = LingqApi("test_key", "test_lang", import_knowns=True)
        assert api.import_knowns == True
