import copy
import re
from unittest.mock import MagicMock


class StrictMock:
    """A base class for mocks that raises errors when unmocked methods are called."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        else:
            raise NotImplementedError(
                f"'{type(self).__name__}' has no attribute '{name}'. If this is a real Anki API attribute, please implement it in 'Tests/mocks.py'."
            )


class MockNote(dict):
    def __init__(self, col, model):
        self.col = col
        self.model = model
        self.note_type_dict = {}

    def note_type(self):
        return self.note_type_dict


class MockCard:
    """A mock of the Anki Card class that has a note() method."""

    def __init__(self, card_data, mock_collection):
        self.card_data = card_data
        self.mock_collection = mock_collection
        self._note = None

    def note(self):
        """Returns a mock note that can be updated."""
        if self._note is None:
            # Create a mock note with the card's data
            self._note = MockNote(self.mock_collection, None)
            self._note["LingqPK"] = str(self.card_data["primary_key"])
            self._note["Front"] = self.card_data["word"]
            self._note["Back"] = self.card_data["translations"]
            self._note["LingqStatus"] = self.card_data["status"]
            self._note["Sentence"] = self.card_data["sentence"]
            self._note["LingqImportance"] = str(self.card_data["importance"])
            self._note.tags = self.card_data.get("tags", [])
        return self._note


class MockMw(StrictMock):
    """
    A mock of the Anki 'mw' (main window) object.
    It simulates the Anki collection database using a Python dictionary
    and is designed to raise errors if the code under test uses a yet
    unmocked part of the Anki mw library.
    """

    def __init__(self, anki_data):
        # Use a deepcopy to ensure each test gets a fresh version of the data
        self._data = copy.deepcopy(anki_data)

        # Expose the necessary sub-modules (col, form)
        self.col = self._MockCollection(self._data)

    class _MockCollection(StrictMock):
        """Mocks the mw.col object, which manages the Anki database."""

        def __init__(self, data):
            self._data = data
            # Start new note/card IDs at a high, arbitrary, fixed number.
            self._next_id = 900000000

            # Expose mocked sub-modules
            self.db = self._MockDb(self._data)
            self.models = self._MockModels(self._data)
            self.decks = self._MockDecks(self._data)
            self.sched = self._MockScheduler(self._data)

        def _get_next_id(self):
            self._next_id += 1
            return self._next_id

        def find_cards(self, query: str):
            """Simulates finding cards based on a query string."""
            deck_match = re.search(r'deck:"([^"]+)"', query)
            pk_match = re.search(r'LingqPK:"([^"]+)"', query)
            deck_name = deck_match.group(1) if deck_match else None
            lingq_pk = pk_match.group(1) if pk_match else None

            if not deck_name or deck_name not in self._data:
                return []

            deck_cards = self._data[deck_name]["cards"]
            found_ids = []
            for card in deck_cards:
                if card["primary_key"] == int(lingq_pk):
                    found_ids.append(card["primary_key"])

            return found_ids

        def get_card(self, card_id: int):
            """Simulates retrieving a single card object."""
            for deck_name, deck_data in self._data.items():
                for card_info in deck_data["cards"]:
                    if str(card_info.get("primary_key")) == str(card_id):
                        # Return a MockCard that has a note() method
                        return MockCard(card_info, self)

            return None  # Card not found

        def add_note(self, note, deck_id: int):
            """Simulates adding a new note to the collection."""
            deck_name = self.decks.name(deck_id)
            if not deck_name:
                return

            new_card_id = self._get_next_id()
            note.id = new_card_id

            card_data = {
                "primary_key": int(note["LingqPK"]),
                "word": note["Front"],
                "translations": note["Back"],
                "status": note["LingqStatus"],
                "tags": note.tags,
                "sentence": note["Sentence"],
                "importance": int(note["LingqImportance"]),
                "interval": 0,  # New cards have an interval of 0
            }
            if "cards" not in self._data[deck_name]:
                self._data[deck_name]["cards"] = []

            self._data[deck_name]["cards"].append(card_data)

        def update_note(self, note):
            """Simulates updating an existing note."""
            pk_to_find = int(note["LingqPK"])
            for deck in self._data.values():
                for card in deck["cards"]:
                    if card["primary_key"] == pk_to_find:
                        card["word"] = note["Front"]
                        card["translations"] = note["Back"]
                        card["status"] = note["LingqStatus"]
                        card["tags"] = note.tags
                        card["sentence"] = note["Sentence"]
                        card["importance"] = int(note["LingqImportance"])
                        return

        class _MockDb(StrictMock):
            def __init__(self, data):
                self._data = data

            def scalar(self, query: str, card_id: int):
                """Simulates retrieving a single value from the db."""
                if "select ivl from cards where id = ?" in query:
                    for deck_data in self._data.values():
                        for card in deck_data["cards"]:
                            if card.get("primary_key") == card_id:
                                return card.get("interval", 0)
                    return 0  # Card not found
                else:
                    raise NotImplementedError(f"Query type not yet mocked: {query}")

        class _MockDecks(StrictMock):
            def __init__(self, data):
                self._data = data

            def all_names_and_ids(self):
                return [MagicMock(name=name, id=data["id"]) for name, data in self._data.items()]

            def id(self, deck_name: str):
                return self._data[deck_name]["id"]

            def name(self, deck_id: int):
                for name, data in self._data.items():
                    if data["id"] == deck_id:
                        return name

        class _MockModels(StrictMock):
            def __init__(self, data):
                self._data = data
                # A simple dict to fake the existence of note types
                self._models = {"lingqAnkiSync": True}

            def by_name(self, model_name: str):
                """Checks if a note type exists."""
                return self._models.get(model_name)

            # The following methods just need to exist and not crash
            def new(self, name):
                return MagicMock()

            def addField(self, model, field):
                pass

            def newField(self, name):
                return MagicMock()

            def new_template(self, name):
                return MagicMock()

            def add_template(self, model, template):
                pass

            def add(self, model):
                pass

            def set_current(self, model):
                pass

            def save(self, model):
                pass

        class _MockScheduler(StrictMock):
            def __init__(self, data):
                self._data = data

            def set_due_date(self, card_ids: list, interval: str):
                """Sets the interval (ivl) for a card."""
                updated_count = 0
                for deck_data in self._data.values():
                    for card in deck_data["cards"]:
                        if card["primary_key"] in card_ids:
                            card["interval"] = int(interval)
                            updated_count += 1
                return updated_count
