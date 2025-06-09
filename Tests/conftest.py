import json
import pytest
from unittest.mock import MagicMock, patch

# You will need to install this library: pip install requests-mock
# It provides the 'requests_mock' fixture automatically.


# --- Test Data Loading Fixtures ---

@pytest.fixture
def lingq_data():
    """Loads mock LingQ data from Tests/test_data/lingq_data.json."""
    with open("Tests/test_data/lingq_data.json") as f:
        content = f.read()
        if not content:
            return {}
        return json.loads(content)


@pytest.fixture
def anki_data():
    """Loads mock Anki data from Tests/test_data/anki_data.json."""
    with open("Tests/test_data/anki_data.json") as f:
        content = f.read()
        if not content:
            return {}
        return json.loads(content)


# --- Mocking Fixtures ---

@pytest.fixture
def mock_mw():
    """
    Mocks the 'mw' (Anki's main window) object from aqt.
    This fixture patches 'mw' where it is used in your AnkiHandler,
    providing a clean mock for each test function.
    """
    # This patch targets 'mw' within the AnkiHandler module.
    # If you use 'mw' in other modules, you may need to add more patches.
    with patch("lingqAnkiSync.AnkiHandler.mw", new_callable=MagicMock) as mock:
        yield mock


# The 'requests_mock' fixture is automatically provided by the 'requests-mock' library.
# To use it, simply add it as an argument to your test function, like so:
#
# def test_api_call(requests_mock):
#     requests_mock.get("http://lingq.com/api/v2/...", json={"key": "value"})
#     # ... your test code that calls the api ... 