from aqt.qt import *
from aqt import mw
from aqt.operations import QueryOp
from anki.notes import Note
from aqt.utils import showInfo
from . import LingqApi, Config, AnkiHandler

# Anki note model name and fields
MODEL_NAME = "Basic"
NOTE_FIELDS = ["Front", "Back"]
lingqs = []

# Anki deck name
DECK_NAME = "My LingQs"

class LingqAnkiSync:
    def __init__(self):
        action = QAction("Import LingQs from LingQ.com", mw)
        action.triggered.connect(lambda: LingQImporter().run())
        self.api_key_field = QLineEdit()
        self.language_code_field = QLineEdit()
        self.deck_selector = QComboBox()
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(QPushButton("Import"), QDialogButtonBox.AcceptRole)
        self.button_box.addButton(QPushButton("Cancel"), QDialogButtonBox.RejectRole)

    def run(self):
        self.dialog = QDialog(mw)
        self.dialog.setWindowTitle("Import LingQs from LingQ.com")
        self.dialog.setWindowModality(Qt.WindowModal)

        self.language_code_field.setPlaceholderText("Language Code")
        self.api_key_field.setPlaceholderText("API Key")
        self.api_key_field.setText(Config.getApiKey())
        self.language_code_field.setText(Config.getLanguageCode())

        # Create deck selector
        self.deck_selector.addItems(self.get_deck_names())

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter LingQ API Key:"))
        layout.addWidget(self.api_key_field)
        layout.addWidget(self.language_code_field)
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

    def create_note(self, word, translation, deckName):
        # Get note model
        model = mw.col.models.byName(MODEL_NAME)
        #deck = mw.col.decks.by_name(deckName)
        note = Note(mw.col, model)
        
        # Set note fields
        note["Front"] = word
        note["Back"] = translation
        deck_id = mw.col.decks.id(deckName)
        note.model()['did'] = deck_id

        # Add note to collection
        mw.col.addNote(note)

    def import_lingqs(self):
        api_key = self.api_key_field.text()
        language_code = self.language_code_field.text()
        Config.setApiKey(api_key)
        Config.setLanguageCode(language_code)

        # Get LingQ data
        op = QueryOp(
            parent = mw,
            op=lambda col: LingqApi.getAllWords(api_key, language_code),
            success=self.CreateCards,
        )
        op.with_progress("Lingq import in progress, please wait.").run_in_background()

        # Import new LingQs into Anki
        
    def CreateCards(self, lingqs):
        deck_name = self.deck_selector.currentText()
        for lingq in lingqs:
            word_key = lingq['term']
            #if word_key not in existing_word_keys:
            if (len(lingq['hints']) > 0):
                translation = lingq['hints'][0]['text']
            pk = lingq['pk']
            AnkiHandler.CreateNote(word_key, translation, pk, deck_name)

        mw.reset()
        showInfo("Import complete!")


# Add menu item
action = QAction("Import LingQs from LingQ.com", mw)
action.triggered.connect(lambda: LingqAnkiSync().run())
mw.form.menuTools.addAction(action)