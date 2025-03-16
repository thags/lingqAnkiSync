# frozen_string_literal: true

import sys, os
sys.path.append(
    os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync")
)
from LingqApi import LingqApi
import pytest

class TestLingqApi:
    def test_should_set_import_knowns_to_true_by_default(self):
        # Arrange & Act
        api = LingqApi("test_key", "test_lang")

        # Assert
        assert api.import_knowns == True

    def test_should_set_import_knowns_to_false_when_specified(self):
        # Arrange & Act
        api = LingqApi("test_key", "test_lang", import_knowns=False)

        # Assert
        assert api.import_knowns == False

    def test_should_set_import_knowns_to_true_when_specified(self):
        # Arrange & Act
        api = LingqApi("test_key", "test_lang", import_knowns=True)

        # Assert
        assert api.import_knowns == True
