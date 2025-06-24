import os
import time
from aqt import mw
from anki.notes import Note
from anki.cards import Card
from typing import List
from .Models.AnkiCard import AnkiCard


def CreateNotesFromCards(cards: List[AnkiCard], deckName: str) -> int:
    return sum(CreateNote(card, deckName) == True for card in cards)


def CreateNote(card: AnkiCard, deckName: str) -> bool:
    if DoesDuplicateCardExistInDeck(card.primaryKey, deckName):
        return False
    modelName = "lingqAnkiSync"
    noteFields = [
        "Front",
        "Back",
        "LingqPK",
        "LingqStatus",
        "Sentence",
        "LingqImportance",
        "FrontAudio",
        "SentenceAudio",
    ]
    CreateNoteTypeIfNotExist(modelName, noteFields)

    model = mw.col.models.byName(modelName)
    note = Note(mw.col, model)

    note["Front"] = card.word
    note["Back"] = "<br>".join(f"{i+1}. {item}" for i, item in enumerate(card.translations))
    note["LingqPK"] = str(card.primaryKey)
    note["LingqStatus"] = str(card.status)
    note.tags = card.tags
    note["Sentence"] = card.sentence
    note["LingqImportance"] = str(card.importance)

    deckId = mw.col.decks.id(deckName)
    note.note_type()["did"] = deckId
    mw.col.addNote(note, deckId)
    if card.interval > 0:
        mw.col.sched.set_due_date([note.id], str(card.interval))
    return True


def DoesDuplicateCardExistInDeck(lingqPk, deckName):
    return len(mw.col.find_cards(f'deck:"{deckName}" LingqPK:"{lingqPk}"')) > 0


def CreateNoteType(name: str, fields: List):
    model = mw.col.models.new(name)

    for field in fields:
        mw.col.models.addField(model, mw.col.models.newField(field))

    template = mw.col.models.newTemplate("lingqAnkiSync")
    resourceFolder = os.path.dirname(__file__) + "/resources"

    with open(resourceFolder + "/style.css", "r") as f:
        model["css"] = f.read()

    with open(resourceFolder + "/front.html", "r") as f:
        template["qfmt"] = f.read()

    with open(resourceFolder + "/back.html", "r") as f:
        template["afmt"] = f.read()

    mw.col.models.addTemplate(model, template)
    mw.col.models.add(model)
    mw.col.models.setCurrent(model)
    mw.col.models.save(model)
    return model


def CreateNoteTypeIfNotExist(noteTypeName: str, noteFields: List):
    if not mw.col.models.byName(noteTypeName):
        CreateNoteType(noteTypeName, noteFields)


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
