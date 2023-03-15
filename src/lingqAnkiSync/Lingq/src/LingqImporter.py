from .LingqModel import Lingq
from .LingqApi import LingqAPI

class LingqImporter:
    def __init__(self, apiKey, languageCode):
        self.LingqApi = LingqAPI(apiKey, languageCode)

    def FormatLingqs(self, lingqs):
        formattedLingqs = []
        for lingq in lingqs:
            primaryKey = lingq['pk']
            word = lingq['term']
            translation = lingq['hints'][0]['text'] if (
                len(lingq['hints']) > 0) else " "
            status = lingq['status']
            extendedStatus = lingq['extended_status']
            lingq = Lingq(primaryKey, word, translation, status, extendedStatus)
            formattedLingqs.append(lingq)
        return formattedLingqs
    
    def GetLingqs(self):
        return self.LingqApi.getAllWords()