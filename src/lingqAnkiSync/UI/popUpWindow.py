from aqt.qt import QLineEdit, QComboBox, QPushButton, QAction, QDialogButtonBox, QDialog, QVBoxLayout, QLabel, Qt
from aqt import mw
from aqt.operations import QueryOp
from aqt.utils import showInfo

from .ActionHandler import ActionHandler


class UI:
    def __init__(self):
        action = QAction("Import LingQs from LingQ.com", mw)
        action.triggered.connect(lambda: UI().run())
        self.api_key_field = QLineEdit()
        self.language_code_field = QLineEdit()
        self.deck_selector = QComboBox()

        self.import_button_box = QDialogButtonBox()
        self.import_button_box.addButton(
            QPushButton("Import"), QDialogButtonBox.AcceptRole)
        self.import_button_box.addButton(
            QPushButton("Cancel"), QDialogButtonBox.RejectRole)

        self.sync_button_box = QDialogButtonBox()
        self.sync_button_box.addButton(QPushButton(
            "Sync to Lingq"), QDialogButtonBox.AcceptRole)
        self.actionHandler = ActionHandler(mw.addonManager)

    def run(self):
        self.dialog = QDialog(mw)
        self.dialog.setWindowTitle("Import LingQs from LingQ.com")
        self.dialog.setWindowModality(Qt.WindowModal)

        self.language_code_field.setPlaceholderText("Language Code")
        self.api_key_field.setPlaceholderText("API Key")
        self.api_key_field.setText(self.actionHandler.GetApiKey())
        self.language_code_field.setText(self.actionHandler.GetLanguageCode())

        self.deck_selector.addItems(self.actionHandler.GetDeckNames())

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter LingQ API Key:"))
        layout.addWidget(self.api_key_field)
        layout.addWidget(self.language_code_field)
        layout.addWidget(QLabel("Select deck to import LingQs into:"))
        layout.addWidget(self.deck_selector)
        layout.addWidget(self.import_button_box)
        layout.addWidget(self.sync_button_box)
        self.dialog.setLayout(layout)

        self.import_button_box.accepted.connect(self.import_lingqs)
        self.import_button_box.rejected.connect(self.dialog.reject)
        self.sync_button_box.accepted.connect(self.SyncLingqsBackground)

        self.dialog.exec_()

    def import_lingqs(self):
        self.configSet()
        deckName = self.deck_selector.currentText()
        op = QueryOp(
            parent=mw,
            op=lambda col: self.actionHandler.ImportLingqsToAnki(deckName),
            success=self.SuccesfulImport,
        )
        op.with_progress(
            "Lingq import in progress, please wait.").run_in_background()
        self.dialog.close()

    def SuccesfulImport(self, importedLingqsCount):
        mw.reset()
        showInfo(f"Import complete on {importedLingqsCount} lingqs!")
        
    def configSet(self):
        api_key = self.api_key_field.text()
        language_code = self.language_code_field.text()
        self.actionHandler.SetConfigs(api_key, language_code)

    def SyncLingqsBackground(self):
        self.configSet()
        deckName = self.deck_selector.currentText()
        op = QueryOp(
            parent=mw,
            op=lambda col: self.actionHandler.SyncLingqStatusToLingq(deckName),
            success=self.SuccesfulSync,
        )
        op.with_progress(
            "Sync to Lingq in progress, please wait.").run_in_background()
        self.dialog.close()

    def SuccesfulSync(self, result):
        showInfo("Sync complete!")


action = QAction("Import LingQs from LingQ.com", mw)
action.triggered.connect(lambda: UI().run())
mw.form.menuTools.addAction(action)
