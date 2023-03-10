from aqt.qt import *
from aqt import mw
from anki.utils import ids2str
from anki.notes import Note
from anki.cards import Card
from aqt.utils import showInfo

from . import LingqApi


# Anki note model name and fields
MODEL_NAME = "Basic"
NOTE_FIELDS = ["Front", "Back"]

# Anki deck name
DECK_NAME = "My LingQs"

class LingQImporter:
    def __init__(self):
        action = QAction("Import LingQs from LingQ.com", mw)
        action.triggered.connect(lambda: LingQImporter().run())
        #gui_hooks.main_window_did_init_menu_bar.append(lambda menuBar: menuBar.addAction(action))
        self.api_key_field = QLineEdit()
        self.user_id_field = QLineEdit()
        self.deck_selector = QComboBox()
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(QPushButton("Import"), QDialogButtonBox.AcceptRole)
        self.button_box.addButton(QPushButton("Cancel"), QDialogButtonBox.RejectRole)

    def run(self):
        self.dialog = QDialog(mw)
        self.dialog.setWindowTitle("Import LingQs from LingQ.com")
        self.dialog.setWindowModality(Qt.WindowModal)

        # Create API key and user ID fields
        self.api_key_field.setPlaceholderText("LingQ API Key")
        self.user_id_field.setPlaceholderText("LingQ User ID")

        # Create deck selector
        self.deck_selector.addItems(self.get_deck_names())

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter LingQ API Key and User ID:"))
        layout.addWidget(self.api_key_field)
        layout.addWidget(self.user_id_field)
        layout.addWidget(QLabel("Select deck to import LingQs into:"))
        layout.addWidget(self.deck_selector)
        layout.addWidget(self.button_box)
        self.dialog.setLayout(layout)

        # Connect signals
        self.button_box.accepted.connect(self.import_lingqs)
        self.button_box.rejected.connect(self.dialog.reject)

        # Show dialog
        self.dialog.exec_()

    def get_deck_names(self):
        return mw.col.decks.all_names()

    # def get_existing_word_keys(self, deck_name):
    #     existing_word_keys = set()
    #     for note_id in mw.col.findNotes(f"deck:'{deck_name}'"):
    #         note = mw.col.getNote(note_id)
    #         if 'LingQ URL:' in note['Notes']:
    #             existing_word_keys.add(note['Word Key'])
    #     return existing_word_keys

    def create_note(self, word, translation, deck_id):
        # Get note model
        model = mw.col.models.byName(MODEL_NAME)
        #deck = mw.col.decks.by_name(deckName)
        note = Note(mw.col, model)
        

        # Set note fields
        note["Front"] = word
        note["Back"] = translation
        #note["Notes"] = notes
        #note["photo"] = deckName
        note.deckId = deck_id

        # Add note to collection
        mw.col.addNote(note)

        return note

    def import_lingqs(self):
        api_key = self.api_key_field.text()
        user_id = self.user_id_field.text()
        deck_name = self.deck_selector.currentText()
        #existing_word_keys = self.get_existing_word_keys(deck_name)

        # Get LingQ data
        lingqs = LingqApi.getAllWords(api_key, "es")

        # Import new LingQs into Anki
        for lingq in lingqs:
            word_key = lingq['term']
            #if word_key not in existing_word_keys:
            try:
                translation = lingq['hints'][0]['text']
                deck_id = deck = mw.col.decks.by_name(deck_name)
                self.create_note(word_key, translation, deck_id)
            except Exception:
                continue

        showInfo("Import complete!")


# Add menu item
action = QAction("Import LingQs from LingQ.com", mw)
action.triggered.connect(lambda: LingQImporter().run())
mw.form.menuTools.addAction(action)