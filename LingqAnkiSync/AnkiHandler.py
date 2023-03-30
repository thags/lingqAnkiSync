from aqt import mw
from anki.notes import Note
from typing import List
from .Models.AnkiCard import AnkiCard

def CreateNotesFromCards(cards: List[AnkiCard], deckName: str) -> int:
    return sum(CreateNote(card, deckName) == True for card in cards)

def CreateNote(card: AnkiCard, deckName: str) -> bool:
    if (DoesDuplicateCardExistInDeck(card.primaryKey , deckName)):
        return False
    modelName = "LingqAnkiSyncModel"
    noteFields = ["Front", "Back", "LingqPK", "LingqStatus", "LingqExtendedStatus", "Sentence", "LingqImportance"]
    CreateNoteTypeIfNotExist(modelName, noteFields, deckName)

    model = mw.col.models.byName(modelName)
    note = Note(mw.col, model)

    note["Front"] = card.word
    note["Back"] = ", ".join(card.translations)
    note["LingqPK"] = str(card.primaryKey)
    note["LingqStatus"] = str(card.status)
    note["LingqExtendedStatus"] = str(card.extended_status)
    note.tags = card.tags
    note["Sentence"] = card.sentence
    note["LingqImportance"] = str(card.importance)

    deck_id = mw.col.decks.id(deckName)
    note.model()['did'] = deck_id
    mw.col.addNote(note)
    if card.interval > 0:
        mw.col.sched.set_due_date([note.id], str(card.interval))
    return True

def DoesDuplicateCardExistInDeck(LingqPK, deckName):
    return len(mw.col.find_cards(f'deck:"{deckName}" LingqPK:"{LingqPK}"')) > 0

def CreateNoteType(name: str, fields: List):
    model = mw.col.models.new(name)

    for field in fields:
        mw.col.models.addField(model, mw.col.models.newField(field))

    template = mw.col.models.newTemplate("lingqAnkiSync")
    template['qfmt'] = "{{Front}}<br>{{Sentence}}"
    template['afmt'] = "{{FrontSide}}<hr id=answer>{{Back}}"
    mw.col.models.addTemplate(model, template)
    mw.col.models.add(model)
    mw.col.models.setCurrent(model)
    mw.col.models.save(model)
    return model

def CreateNoteTypeIfNotExist(noteTypeName: str, noteFields: List, deckName: str):
    if not mw.col.models.byName(noteTypeName):
        CreateNoteType(noteTypeName, noteFields)

def GetAllCardsInDeck(deckName: str) -> List[AnkiCard]:
    cards = []
    cardIds = mw.col.find_cards(f'deck:"{deckName}"')
    for cardId in cardIds:
        card = mw.col.get_card(cardId)
        card = _CreateAnkiCardObject(card, cardId)
        cards.append(card)
    return cards

def GetAllDeckNames() -> List[str]:
    return mw.col.decks.all_names()

def GetIntervalFromCard(cardId) -> int:
    interval = mw.col.db.scalar("select ivl from cards where id = ?", cardId)
    return 0 if interval is None else interval

def _CreateAnkiCardObject(card, cardId) -> AnkiCard:
    return AnkiCard(
        card.note()["LingqPK"],
        card.note()["Front"],
        card.note()["Back"],
        GetIntervalFromCard(cardId),
        card.note()["LingqStatus"],
        card.note()["LingqExtendedStatus"],
        card.note().tags,
        card.note()["Sentence"],
        card.note()["LingqImportance"]
    )