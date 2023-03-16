from .LingqApi import LingqAPI

class LingqImporter:
    def __init__(self, apiKey, languageCode):
        self.LingqApi = LingqAPI(apiKey, languageCode)

    def FormatLingqs(self, lingqs):
        return [
            {
                "PrimaryKey": lingq['pk'],
                "Word": lingq['term'],
                "Translation": lingq['hints'][0]['text']
                    if (len(lingq['hints']) > 0)
                    else " ",
                "Interval": lingq['status'],
                "ExtendedStatus": lingq['extended_status'],
            }
            for lingq in lingqs
        ]
    
    def GetLingqs(self):
        return self.LingqApi.getAllWords()