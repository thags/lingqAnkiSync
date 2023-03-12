from datetime import datetime
import requests, string

def getSinglePageResult(apiKey, url):
    headers = {'Authorization': 'Token {}'.format(apiKey)}
    words_response = requests.get(url, headers=headers)
    words_response.raise_for_status()
    return words_response

def getAllWords(apiKey, languageCode):
    nextUrl = "https://www.lingq.com/api/v2/{}/cards".format(languageCode)
    lingqs = []
    while (nextUrl != None):
        words_response = getSinglePageResult(apiKey, nextUrl)
        words = words_response.json()['results']
        lingqs.extend(words)
        nextUrl = words_response.json()['next']
        break
    return lingqs

def updateLingqStatus(lingqPrimaryKey, knownStatus, apiKey, languageCode):
    headers = {'Authorization': 'Token {}'.format(apiKey)}
    url = f"https://www.lingq.com/api/v2/{languageCode}/cards/{lingqPrimaryKey}/"
    response = requests.patch(url, headers=headers, data={"status": knownStatus})
    response.raise_for_status()