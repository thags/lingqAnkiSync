import os
import time
from aqt import mw
from anki.notes import Note
from anki.cards import Card
from typing import List
from .Models.AnkiCard import AnkiCard


_contextReverseLinks = {
    "ar": "https://context.reverso.net/translation/arabic-english/{{Front}}",
    "de": "https://context.reverso.net/translation/german-english/{{Front}}",
    "es": "https://context.reverso.net/translation/spanish-english/{{Front}}",
    "fr": "https://context.reverso.net/translation/french-english/{{Front}}",
    "he": "https://context.reverso.net/translation/hebrew-english/{{Front}}",
    "it": "https://context.reverso.net/translation/italian-english/{{Front}}",
    "ja": "https://context.reverso.net/translation/japanese-english/{{Front}}",
    "ko": "https://context.reverso.net/translation/korean-english/{{Front}}",
    "nl": "https://context.reverso.net/translation/dutch-english/{{Front}}",
    "pl": "https://context.reverso.net/translation/polish-english/{{Front}}",
    "pt": "https://context.reverso.net/translation/portuguese-english/{{Front}}",
    "ro": "https://context.reverso.net/translation/romanian-english/{{Front}}",
    "ru": "https://context.reverso.net/translation/russian-english/{{Front}}",
    "sv": "https://context.reverso.net/translation/swedish-english/{{Front}}",
    "tr": "https://context.reverso.net/translation/turkish-english/{{Front}}",
    "uk": "https://context.reverso.net/translation/ukrainian-english/{{Front}}",
    "zh": "https://context.reverso.net/translation/chinese-english/{{Front}}",
}

_noteFields = [
    "Front",
    "Back",
    "LingqPK",
    "LingqStatus",
    "Sentence",
    "LingqImportance",
    "FrontAudio",
    "SentenceAudio",
]

def _GetModelName(languageCode: str) -> str:
    return f"lingqAnkiSync_{languageCode}"


def CreateNotesFromCards(
    cards: List[AnkiCard], deckName: str, languageCode: str
) -> int:
    return sum(CreateNote(card, deckName, languageCode) == True for card in cards)


def CreateNote(card: AnkiCard, deckName: str, languageCode: str) -> bool:
    if DoesDuplicateCardExistInDeck(card.primaryKey, deckName):
        return False
    CreateNoteTypeIfNotExist(languageCode)

    model = mw.col.models.byName(_GetModelName(languageCode))
    note = Note(mw.col, model)

    note["Front"] = card.word
    note["Back"] = "<br>".join(
        f"{i+1}. {item}" for i, item in enumerate(card.translations)
    )
    note["LingqPK"] = str(card.primaryKey)
    note["LingqStatus"] = str(card.status)
    note.tags = card.tags
    note["Sentence"] = card.sentence
    note["LingqImportance"] = str(card.importance)

    deck_id = mw.col.decks.id(deckName)
    note.note_type()["did"] = deck_id
    mw.col.add_note(note, deck_id)
    if card.interval > 0:
        mw.col.sched.set_due_date([note.id], str(card.interval))
    return True


def DoesDuplicateCardExistInDeck(lingqPk, deckName):
    return len(mw.col.find_cards(f'deck:"{deckName}" LingqPK:"{lingqPk}"')) > 0


def CreateNoteType(languageCode: str):
    model = mw.col.models.new(_GetModelName(languageCode))

    for field in _noteFields:
        mw.col.models.addField(model, mw.col.models.newField(field))

    template = mw.col.models.newTemplate(_GetModelName(languageCode))
    resourceFolder = os.path.join(os.path.dirname(__file__), "resources")

    with open(os.path.join(resourceFolder, "style.css"), "r") as f:
        model["css"] = f.read()

    with open(os.path.join(resourceFolder, "front.html"), "r") as f:
        template["qfmt"] = f.read()

    with open(os.path.join(resourceFolder, "back.html"), "r") as f:
        html = f.read()
        if languageCode and languageCode in _contextReverseLinks:
            template["afmt"] = html.replace(
                '<div class="ReverseContextPlaceholder"></div>',
                f"""
                <div class="back">
                    <a href="{_contextReverseLinks[languageCode]}">Reverse Context</a>
                </div>
                """,
            )
        else:
            template["afmt"] = html

    mw.col.models.addTemplate(model, template)
    mw.col.models.add(model)
    mw.col.models.setCurrent(model)
    mw.col.models.save(model)
    return model


def CreateNoteTypeIfNotExist(languageCode: str):
    if not mw.col.models.byName(_GetModelName(languageCode)):
        CreateNoteType(languageCode)


def UpdateCardStatus(deckName: str, lingqPk: int, status: str):
    cardId = mw.col.find_cards(f'deck:"{deckName}" LingqPK:"{lingqPk}"')[0]
    card = mw.col.get_card(cardId)
    card.note()["LingqStatus"] = status
    mw.col.update_note(card.note())

    # Anki seems to miss a few of them if the updates aren't spaced out. This isn't a perfect solution
    time.sleep(0.1)

def GetAllCardsInDeck(deckName: str) -> List[AnkiCard]:
    cards = []
    cardIds = mw.col.find_cards(f'deck:"{deckName}"')
    for cardId in cardIds:
        card = mw.col.get_card(cardId)
        card = _CreateAnkiCardObject(card, cardId)
        cards.append(card)
    return cards


def GetAllDeckNames() -> List[str]:
    return [x.name for x in mw.col.decks.all_names_and_ids()]


def GetIntervalFromCard(cardId: int) -> int:
    interval = mw.col.db.scalar("select ivl from cards where id = ?", cardId)
    return 0 if interval is None else interval


def _CreateAnkiCardObject(card: Card, cardId: int) -> AnkiCard:
    return AnkiCard(
        primaryKey=int(card.note()["LingqPK"]),
        word=card.note()["Front"],
        translations=card.note()[
            "Back"
        ],  # TODO this needs to split or parse out the "1. [translation1] 2. [translation2]" etc
        interval=GetIntervalFromCard(cardId),
        status=card.note()["LingqStatus"],
        tags=card.note().tags,
        sentence=card.note()["Sentence"],
        importance=card.note()["LingqImportance"],
    )
