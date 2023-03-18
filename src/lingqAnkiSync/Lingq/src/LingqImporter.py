from .....LingqAnkiSync.Models.Lingq import Lingq
import json

class LingqImporter:
    def __init__(self, LingqApi):
        self.LingqApi = LingqApi

    def FormatLingqs(self, jsonLingqs: json) -> list[Lingq]:
        formattedLingqs = []
        for lingq in jsonLingqs:
            formattedLingq = Lingq(
                lingq['pk'],
                lingq['term'],
                lingq['hints'][0]['text']
                    if (len(lingq['hints']) > 0)
                    else " ",
                lingq['status'],
                lingq['extended_status']
            )
            formattedLingqs.append(formattedLingq)
        return formattedLingqs
    
    def GetFormattedLingqs(self) -> list[Lingq]:
        return self.FormatLingqs(self.LingqApi.getAllWords())