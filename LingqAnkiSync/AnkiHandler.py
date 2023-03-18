from aqt import mw
from anki.notes import Note
from .Models.AnkiCard import AnkiCard

def CreateNotesFromCards(cards: list[AnkiCard], deckName: str) -> int:
    notesCreated = 0
    for card in cards:
        if (CreateNote(card, deckName) == True):
            notesCreated += 1
    return notesCreated

def CreateNote(card: AnkiCard, deckName: str) -> bool:
    if (DoesDuplicateCardExistInDeck(card.primaryKey , deckName)):
        return False
    modelName = "LingqAnkiSync"
    noteFields = ["Front", "Back", "LingqPK"]
    CreateNoteTypeIfNotExist(modelName, noteFields, deckName)

    model = mw.col.models.byName(modelName)
    note = Note(mw.col, model)

    note["Front"] = card.word
    note["Back"] = card.translation
    note["LingqPK"] = str(card.primaryKey)

    deck_id = mw.col.decks.id(deckName)
    note.model()['did'] = deck_id
    mw.col.addNote(note)
    mw.col.sched.set_due_date([note.id], str(card.interval))
    return True

def DoesDuplicateCardExistInDeck(LingqPK, deckName):
    return len(mw.col.findCards(f'deck:"{deckName}" LingqPK:"{LingqPK}"')) > 0

def CreateNoteType(name: str, fields: list):
    model = mw.col.models.new(name)

    for field in fields:
        mw.col.models.addField(model, mw.col.models.newField(field))

    template = mw.col.models.newTemplate("lingqAnkiSyncTemplate")
    template['qfmt'] = "{{Front}}"
    template['afmt'] = "{{FrontSide}}<hr id=answer>{{Back}}"
    mw.col.models.addTemplate(model, template)
    mw.col.models.add(model)
    mw.col.models.setCurrent(model)
    mw.col.models.save(model)
    return model

def CreateNoteTypeIfNotExist(noteTypeName: str, noteFields: list, deckName: str):
    if not mw.col.models.byName(noteTypeName):
        CreateNoteType(noteTypeName, noteFields)

def GetAllCardsInDeck(deckName: str):
    deck_id = mw.col.decks.id(deckName)
    mw._selectedDeck = deck_id
    cards = []
    cardIds = mw.col.findCards(f'deck:"{deckName}"')
    for cardId in cardIds:
        card = mw.col.get_card(cardId)
        card = _CreateAnkiCardObject(card, cardId)
        cards.append(card)
    return cards

def GetAllDeckNames():
    return mw.col.decks.all_names()

def GetIntervalFromCard(cardId):
    interval = mw.col.db.scalar("select ivl from cards where id = ?", cardId)
    return 0 if interval is None else interval

def _CreateAnkiCardObject(card, cardId):
    return AnkiCard(
        card.note()["LingqPK"],
        card.note()["Front"],
        card.note()["Back"],
        GetIntervalFromCard(cardId)
    )