import json
import requests

def getSinglePageResult(apiKey, url):
    headers = {'Authorization': 'Token {}'.format(apiKey)}
    words_response = requests.get(url, headers=headers)
    words_response.raise_for_status()  # raise an exception if the request was unsuccessful
    return words_response

def getAllWords(apiKey, languageCode):
    nextUrl = "https://www.lingq.com/api/v2/{}/cards".format(languageCode)
    lingqs = []
    while (nextUrl != None):
        words_response = getSinglePageResult(apiKey, nextUrl)
        words = words_response.json()['results']
        lingqs.extend(words)
        nextUrl = words_response.json()['next']
    return lingqs

# def convertToLingqObjects(lingqsInJson):
#     convertedLinqs = []
#     for lingq in lingqsInJson:
#         converted = json.loads(lingq, object_hook=lambda lingq: SimpleNamespace(**lingq))
#         convertedLinqs.extend(converted);
#     return convertedLinqs

def convertLingqsToAnkiCards(self):
    cards = []
    for lingq in self.lingqs:
        # create a new Anki card with the word as the front and the definition as the back
        print(lingq['words'][0])
        card = {
          'id': lingq['pk'],
          'front': lingq['term'],
          'back': lingq['hints'][0]['text'],
          'status': lingq['status'],
          'notes': lingq['notes'],
          'sentence': lingq['fragment'],
        }
        cards.extend(card)
    return cards

# create Anki cards for each word
# for word in words:
#   # create a new Anki card with the word as the front and the definition as the back
#   print(word['words'][0])
#   card = {
#     'id': word['pk'],
#     'front': word['term'],
#     'back': word['hints'][0]['text'],
#     'status': word['status'],
#     'notes': word['notes'],
#     'sentence': word['fragment'],
#   }