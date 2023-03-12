import array
import string
from aqt import mw
from anki.notes import Note


def CreateNote(word, translation, lingqPk, dueDate, deckName):
    modelName = "LingqAnkiSync"
    noteFields = ["Front", "Back", "LingqPK"]
    CreateNoteTypeIfNotExist(modelName, noteFields, deckName)
    # Get note model
    model = mw.col.models.byName(modelName)
    #deck = mw.col.decks.by_name(deckName)
    note = Note(mw.col, model)
    
    # Set note fields
    note["Front"] = word
    note["Back"] = translation
    note["LingqPK"] = str(lingqPk)
    #Set due date of note
    
    deck_id = mw.col.decks.id(deckName)
    note.model()['did'] = deck_id
    # Add note to collection
    mw.col.addNote(note)
    mw.col.sched.set_due_date([note.id], dueDate)
    
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
    
#check if note type already exists
def CreateNoteTypeIfNotExist(noteTypeName: string, noteFields: array, deckName: string):
    if not mw.col.models.byName(noteTypeName):
        CreateNoteType(noteTypeName, noteFields)
        
def GetAllCardsInDeck(deckName: string):
    return mw.col.findNotes(f"deck:'{deckName}'")
