import json
import pytest
from unittest.mock import patch
from .mock_anki import MockMw, MockNote
from .mock_lingq_server import LingqApiRestServerMock


@pytest.fixture
def lingqData():
    with open("Tests/data/lingq_data.json") as f:
        content = f.read()
        if not content:
            return {}
        return json.loads(content)


@pytest.fixture
def ankiData():
    with open("Tests/data/anki_data.json") as f:
        return json.loads(f.read())


@pytest.fixture
def mockMw(ankiData):
    """
    Provides a fully functional, isolated mock of Anki's 'mw' object.
    It is pre-loaded with data from the 'anki_data' fixture.
    """
    mw_instance = MockMw(ankiData)
    with patch("LingqAnkiSync.AnkiHandler.mw", mw_instance), patch(
        "LingqAnkiSync.AnkiHandler.Note", MockNote
    ):
        yield mw_instance


@pytest.fixture
def mockLingqServer(lingqData, requests_mock):
    """
    Provides a fully functional mock of the LingQ REST API.
    It is pre-loaded with data from the 'lingqData' fixture and uses requests-mock
    to intercept HTTP calls to the LingQ API endpoints.
    """
    lingq_mock = LingqApiRestServerMock(lingqData, requests_mock)
    yield lingq_mock
