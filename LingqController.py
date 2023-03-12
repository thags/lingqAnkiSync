from . import Helpers, AnkiHandler, LingqApi

class Lingq:
    def __init__(self, primarykey, word, translation, status):
        self.primaryKey = primarykey
        self.word = word
        self.translation = translation
        self.status = status
        

def CreateCardsFromLingqs(lingqs, deckName):
    for lingq in lingqs:
        primaryKey = lingq['pk']
        word = lingq['term']
        if (len(lingq['hints']) > 0):
            translation = lingq['hints'][0]['text']
        status = lingq['status']
        lingq = Lingq(primaryKey, word, translation, status)
        CreateCardFromLingq(lingq, deckName)
        
def CreateCardFromLingq(Lingq, deckName):
    dueInterval = str(Helpers.convertLinqStatusToAnkiDueDate(Lingq.status))
    AnkiHandler.CreateNote(Lingq.word, Lingq.translation, Lingq.primaryKey, dueInterval, deckName)
    
def ImportLingqs(apiKey, languageCode, deckName):
    lingqs = LingqApi.getAllWords(apiKey, languageCode)
    CreateCardsFromLingqs(lingqs, deckName)
    return len(lingqs)