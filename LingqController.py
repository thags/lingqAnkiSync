from . import Helpers, AnkiHandler, LingqApi
from aqt.utils import showInfo

class Lingq:
    def __init__(self, primarykey, word, translation, status, extendedStatus):
        self.primaryKey = primarykey
        self.word = word
        self.translation = translation
        self.status = status
        self.extendedStatus = extendedStatus

def CreateCardsFromLingqs(lingqs, deckName):
    for lingq in lingqs:
        primaryKey = lingq['pk']
        word = lingq['term']
        if (len(lingq['hints']) > 0):
            translation = lingq['hints'][0]['text']
        status = lingq['status']
        extendedStatus = lingq['extended_status']
        lingq = Lingq(primaryKey, word, translation, status, extendedStatus)
        CreateCardFromLingq(lingq, deckName)
        
def CreateCardFromLingq(Lingq, deckName):
    if (Lingq.extendedStatus == 3 and Lingq.status == 3): Lingq.status = 4
    dueInterval = str(Helpers.convertLinqStatusToAnkiDueDate(Lingq.status))
    if (Lingq.translation == None or Lingq.translation == ""): Lingq.translation = " "
    AnkiHandler.CreateNote(Lingq.word, Lingq.translation, Lingq.primaryKey, dueInterval, deckName)
    
def ImportLingqs(apiKey, languageCode, deckName):
    lingqs = LingqApi.getAllWords(apiKey, languageCode)
    CreateCardsFromLingqs(lingqs, deckName)
    return len(lingqs)

def SyncLingq(lingqPrimaryKey, apiKey, languageCode, interval):
    knownStatus = Helpers.convertAnkiIntervalToLingqStatus(interval)
    if (knownStatus < 0): return
    shouldUpdateLingq = ShouldUpdateLingqStatus(lingqPrimaryKey, knownStatus, apiKey, languageCode)
    if (shouldUpdateLingq == True):
        LingqApi.updateLingqStatus(lingqPrimaryKey, apiKey, languageCode, knownStatus)
        showInfo(f"updated lingq status for {lingqPrimaryKey}")
    else:
        showInfo(f"did not update lingq status for {lingqPrimaryKey}")
        return

def ShouldUpdateLingqStatus(lingqPrimaryKey, knownStatus, apiKey, languageCode):
    if (apiKey == None or apiKey == ""): return False
    if (languageCode == None or languageCode == ""): return False
    if (lingqPrimaryKey == None or lingqPrimaryKey == ""): return False
    lingqCurrentStatus = LingqApi.getLingqStatus(lingqPrimaryKey, apiKey, languageCode)
    if (int(lingqCurrentStatus) < int(knownStatus)):
        showInfo(f"lingq status is {lingqCurrentStatus} and known status is {knownStatus}")
        return True
    else:
        showInfo(f"false: lingq status is {lingqCurrentStatus} and known status is {knownStatus}")
        return False
    

