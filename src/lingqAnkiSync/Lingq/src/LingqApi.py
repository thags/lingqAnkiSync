import requests

class LingqAPI:
    def __init__(self, apiKey, languageCode):
        self.apiKey = apiKey
        self.languageCode = languageCode
        self.baseUrl = f"https://www.lingq.com/api/v2/{languageCode}/cards"
    
    def getSinglePageResult(self, url):
        headers = {'Authorization': f'Token {self.apiKey}'}
        words_response = requests.get(url, headers=headers)
        words_response.raise_for_status()
        return words_response

    def getAllWords(self):
        nextUrl = self.baseUrl
        lingqs = []
        while (nextUrl != None):
            words_response = self.getSinglePageResult(nextUrl)
            words = words_response.json()['results']
            lingqs.extend(words)
            nextUrl = words_response.json()['next']
        return lingqs

    def updateLingqStatus(self, lingq):
        if (lingq["extendedStatus"] is None): lingq["extendedStatus"] = 0
        if (lingq["status"] == 4):
            lingq["extendedStatus"] = 3
            lingq["status"] = 3
        headers = {"Authorization": f"Token {self.apiKey}"}
        pk = lingq["PrimaryKey"]
        url = f"{self.baseUrl}/{pk}/"
        response = requests.patch(url, headers=headers, data={
                                  "status": lingq["status"], "extended_status": lingq["extendedStatus"]})
        response.raise_for_status()

    def getLingqStatus(self, lingqPrimaryKey):
        url = f"{self.baseUrl}/{lingqPrimaryKey}/"
        response = self.getSinglePageResult(url)
        status = response.json()['status']
        extendedStatus = response.json()['extended_status']
        if (extendedStatus == 3 and status == 3):
            status = 4
        return status