from . import Helpers, AnkiHandler, LingqApi

class Lingq:
    def __init__(self, primarykey, word, translation, status, extendedStatus):
        self.primaryKey = primarykey
        self.word = word
        self.translation = translation
        self.status = status
        self.extendedStatus = extendedStatus

def CreateCardsFromLingqs(lingqs, deckName) -> int:
    cardsCreated = 0
    for lingq in lingqs:
        primaryKey = lingq['pk']
        word = lingq['term']
        if (len(lingq['hints']) > 0):
            translation = lingq['hints'][0]['text']
        else:
            translation = " "
        status = lingq['status']
        extendedStatus = lingq['extended_status']
        lingq = Lingq(primaryKey, word, translation, status, extendedStatus)
        if (CreateCardFromLingq(lingq, deckName) == True):
            cardsCreated += 1
            
    return cardsCreated
        
def CreateCardFromLingq(Lingq, deckName):
    if (Lingq.extendedStatus == 3 and Lingq.status == 3): Lingq.status = 4
    dueInterval = str(Helpers.convertLinqStatusToAnkiDueDate(Lingq.status))
    didCreateCard = AnkiHandler.CreateNote(Lingq.word, Lingq.translation, Lingq.primaryKey, dueInterval, deckName)
    return didCreateCard
    
def ImportLingqs(apiKey, languageCode, deckName):
    lingqs = LingqApi.getAllWords(apiKey, languageCode)
    cardsCreated = CreateCardsFromLingqs(lingqs, deckName)
    return cardsCreated

def SyncLingq(lingqPrimaryKey, apiKey, languageCode, interval):
    knownStatus = Helpers.convertAnkiIntervalToLingqStatus(interval)
    if (knownStatus < 0): return
    shouldUpdateLingq = ShouldUpdateLingqStatus(lingqPrimaryKey, knownStatus, apiKey, languageCode)
    if (shouldUpdateLingq == True):
        LingqApi.updateLingqStatus(lingqPrimaryKey, apiKey, languageCode, knownStatus)
    else:
        return

def ShouldUpdateLingqStatus(lingqPrimaryKey, knownStatus, apiKey, languageCode):
    if (apiKey == None or apiKey == ""): return False
    if (languageCode == None or languageCode == ""): return False
    if (lingqPrimaryKey == None or lingqPrimaryKey == ""): return False
    lingqCurrentStatus = LingqApi.getLingqStatus(lingqPrimaryKey, apiKey, languageCode)
    if (int(lingqCurrentStatus) < int(knownStatus)):
        return True
    else:
        return False
    

