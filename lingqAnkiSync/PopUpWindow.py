from aqt.qt import (
    QLineEdit,
    QComboBox,
    QPushButton,
    QAction,
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    Qt,
    QCheckBox,
)
from aqt import mw
from aqt.operations import QueryOp
from aqt.utils import showInfo

from .UIActionHandler import ActionHandler


class UI:
    def __init__(self):
        action = QAction("Import LingQs from LingQ.com", mw)
        action.triggered.connect(lambda: UI().Run())
        self.apiKeyField = QLineEdit()
        self.languageCodeField = QLineEdit()
        self.importKnownsBox = QCheckBox("Also import known LingQs")
        self.deckSelector = QComboBox()

        self.importButtonBox = QDialogButtonBox()
        self.importButtonBox.addButton(
            QPushButton("Import"), QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.importButtonBox.addButton(
            QPushButton("Cancel"), QDialogButtonBox.ButtonRole.RejectRole
        )

        self.downgradeLingqsBox = QCheckBox("Allow Sync to downgrade LingQs")
        self.syncButtonBox = QDialogButtonBox()
        self.syncButtonBox.addButton(
            QPushButton("Sync to Lingq"), QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.actionHandler = ActionHandler(mw.addonManager)

    def Run(self):
        self.dialog = QDialog(mw)
        self.dialog.setWindowTitle("Import LingQs from LingQ.com")
        self.dialog.setWindowModality(Qt.WindowModality.WindowModal)

        self.languageCodeField.setPlaceholderText("Language Code")
        self.apiKeyField.setPlaceholderText("API Key")
        self.apiKeyField.setText(self.actionHandler.GetApiKey())
        self.languageCodeField.setText(self.actionHandler.GetLanguageCode())

        self.deckSelector.addItems(self.actionHandler.GetDeckNames())

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter LingQ API Key:"))
        layout.addWidget(self.apiKeyField)
        layout.addWidget(self.languageCodeField)
        layout.addWidget(self.importKnownsBox)
        layout.addWidget(QLabel("Select deck to import LingQs into:"))
        layout.addWidget(self.deckSelector)
        layout.addWidget(self.importButtonBox)
        layout.addWidget(self.downgradeLingqsBox)
        layout.addWidget(self.syncButtonBox)
        self.dialog.setLayout(layout)

        self.importButtonBox.accepted.connect(self.ImportLingqs)
        self.importButtonBox.rejected.connect(self.dialog.reject)
        self.syncButtonBox.accepted.connect(self.SyncLingqsBackground)

        self.dialog.exec()

    def ImportLingqs(self):
        self.ConfigSet()
        deckName = self.deckSelector.currentText()
        importKnowns = self.importKnownsBox.isChecked()
        op = QueryOp(
            parent=mw,
            op=lambda col: self.actionHandler.ImportLingqsToAnki(deckName, importKnowns),
            success=self.SuccesfulImport,
        )
        op.with_progress("Lingq import in progress, please wait.").run_in_background()
        self.dialog.close()

    def SuccesfulImport(self, importedLingqsCount):
        mw.reset()
        showInfo(f"Import complete on {importedLingqsCount} lingqs!")

    def ConfigSet(self):
        apiKey = self.apiKeyField.text()
        languageCode = self.languageCodeField.text()
        self.actionHandler.SetConfigs(apiKey, languageCode)

    def SyncLingqsBackground(self):
        self.ConfigSet()
        deckName = self.deckSelector.currentText()
        downgrade = self.downgradeLingqsBox.isChecked()

        def ProgressCallback(current, total, word, rateLimitSeconds=None):
            """
            Progress callback that handles both normal progress and rate limit notifications

            Args:
                current: Current progress count
                total: Total items to process
                rateLimitSeconds: Integer seconds remaining if we're in a rate limit wait, None otherwise  
            """
            if rateLimitSeconds:
                mw.taskman.run_on_main(
                    lambda: mw.progress.update(
                        label=f'Syncing {current}/{total} - "{word}" <br><span style="font-weight: bold;">⚠️ LingQ API rate limit - waiting {rateLimitSeconds} seconds</span>',
                        value=current,
                        max=total,
                    )
                )
            else:
                mw.taskman.run_on_main(
                    lambda: mw.progress.update(
                        label=f'Syncing {current}/{total} - "{word}"',
                        value=current,
                        max=total,
                    )
                )

        op = QueryOp(
            parent=mw,
            op=lambda col: self.actionHandler.SyncLingqStatusToLingq(
                deckName,
                downgrade,
                progressCallback=ProgressCallback,
            ),
            success=self.SuccesfulSync,
        )
        op.with_progress("Sync to Lingq in progress, please wait.").run_in_background()
        self.dialog.close()

    def SuccesfulSync(self, result):
        mw.reset()
        showInfo(f"Sync complete! {result[0]} lingqs increased and {result[1]} decreased!")


def InitializeAnkiMenu():
    action = QAction("Import LingQs from LingQ.com", mw)
    action.triggered.connect(lambda: UI().Run())
    mw.form.menuTools.addAction(action)
