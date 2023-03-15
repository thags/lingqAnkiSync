from datetime import datetime
import requests
import string


def getSinglePageResult(apiKey, url):
    headers = {'Authorization': f'Token {apiKey}'}
    words_response = requests.get(url, headers=headers)
    words_response.raise_for_status()
    return words_response


def getAllWords(apiKey, languageCode):
    nextUrl = f"https://www.lingq.com/api/v2/{languageCode}/cards"
    lingqs = []
    while (nextUrl != None):
        words_response = getSinglePageResult(apiKey, nextUrl)
        words = words_response.json()['results']
        lingqs.extend(words)
        nextUrl = words_response.json()['next']
    return lingqs


def updateLingqStatus(lingqPrimaryKey, apiKey, languageCode, knownStatus):
    extendedStatus = 0
    if (knownStatus == 4):
        extendedStatus = 3
        knownStatus = 3
    headers = {"Authorization": f"Token {apiKey}"}
    url = f"https://www.lingq.com/api/v2/{languageCode}/cards/{lingqPrimaryKey}/"
    response = requests.patch(url, headers=headers, data={
                              "status": knownStatus, "extended_status": extendedStatus})
    response.raise_for_status()


def getLingqStatus(lingqPrimaryKey, apiKey, languageCode):
    url = f"https://www.lingq.com/api/v2/{languageCode}/cards/{lingqPrimaryKey}/"
    response = getSinglePageResult(apiKey, url)
    status = response.json()['status']
    extendedStatus = response.json()['extended_status']
    if (extendedStatus == 3 and status == 3):
        status = 4
    return status
