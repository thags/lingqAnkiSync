from aqt.qt import *
from aqt import mw
from aqt.operations import QueryOp
from aqt.utils import showInfo
from . import Config, LingqController, AnkiHandler

# Anki note model name and fields
MODEL_NAME = "Basic"
NOTE_FIELDS = ["Front", "Back"]
lingqs = []

# Anki deck name
DECK_NAME = "My LingQs"

class LingqAnkiSync:
    def __init__(self):
        action = QAction("Import LingQs from LingQ.com", mw)
        action.triggered.connect(lambda: LingqAnkiSync().run())
        self.api_key_field = QLineEdit()
        self.language_code_field = QLineEdit()
        self.deck_selector = QComboBox()
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(QPushButton("Sync"), QDialogButtonBox.AcceptRole)
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
        self.deck_selector.addItems(AnkiHandler.GetAllDeckNames())

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

    def import_lingqs(self):
        api_key = self.api_key_field.text()
        language_code = self.language_code_field.text()
        Config.setApiKey(api_key)
        Config.setLanguageCode(language_code)
        deckName = self.deck_selector.currentText()
        # Get LingQ data
        op = QueryOp(
            parent = mw,
            op=lambda col: LingqController.ImportLingqs(api_key, language_code, deckName),
            success=self.SuccesfulImport,
        )
        op.with_progress("Lingq import in progress, please wait.").run_in_background()
        
    def SuccesfulImport(self, importedLingqsCount):
        mw.reset()
        showInfo(f"Import complete on {importedLingqsCount} lingqs!")
        #close the dialog
        self.dialog.close()


# Add menu item
action = QAction("Import LingQs from LingQ.com", mw)
action.triggered.connect(lambda: LingqAnkiSync().run())
mw.form.menuTools.addAction(action)