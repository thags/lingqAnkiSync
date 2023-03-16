import array
import string
from aqt import mw
from anki.notes import Note
from ..utils.Helpers import Helpers

def CreateNotesWithInterval(words, deckName):
    notesCreated = 0
    for word in words:
        if (CreateNoteWithInvterval(
            word["Word"],
            word["Translation"],
            word["PrimaryKey"],
            word["Interval"],
            deckName) == True):
            notesCreated += 1
    return notesCreated

def CreateNoteWithInvterval(word, translation, lingqPk, dueDate, deckName):
    if (DoesDuplicateCardExistInDeck(lingqPk, deckName)):
        return False
    modelName = "LingqAnkiSync"
    noteFields = ["Front", "Back", "LingqPK"]
    CreateNoteTypeIfNotExist(modelName, noteFields, deckName)

    model = mw.col.models.byName(modelName)
    note = Note(mw.col, model)

    note["Front"] = word
    note["Back"] = translation
    note["LingqPK"] = str(lingqPk)

    deck_id = mw.col.decks.id(deckName)
    note.model()['did'] = deck_id
    mw.col.addNote(note)
    mw.col.sched.set_due_date([note.id], str(dueDate))
    return True


def DoesDuplicateCardExistInDeck(lingqPk, deckName):
    return len(mw.col.findCards(f'deck:"{deckName}" LingqPK:"{lingqPk}"')) > 0


def CreateNoteType(name: string, fields: array):
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


def CreateNoteTypeIfNotExist(noteTypeName: string, noteFields: array, deckName: string):
    if not mw.col.models.byName(noteTypeName):
        CreateNoteType(noteTypeName, noteFields)


def GetAllCardsInDeck(deckName: string):
    deck_id = mw.col.decks.id(deckName)
    mw._selectedDeck = deck_id
    cards = []
    cardIds = mw.col.findCards(f'deck:"{deckName}"')
    for cardId in cardIds:
        card = mw.col.get_card(cardId)
        cards.append(card)
    return cards
        

def GetAllLingqsInDeck(deckName: string):
    return Helpers().ConvertAnkiCardsToLingqs(GetAllCardsInDeck(deckName))

def GetAllDeckNames():
    return mw.col.decks.all_names()

def GetPrimaryKeyFromCard(card):
    return card.note()["LingqPK"]

def GetDueDateFromCard(card):
    interval = mw.col.db.scalar("select ivl from cards where id = ?", card.id)
    return 0 if interval is None else interval