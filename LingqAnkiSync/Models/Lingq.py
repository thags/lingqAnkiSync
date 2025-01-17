class Lingq:
    def __init__(self, primarykey, word, translations, status, extendedStatus, tags, fragment, importance, previousStatus = None, popularity = 0):
        self.primaryKey = primarykey
        self.word = word
        self.translations = translations
        self.status = status
        self.extended_status = extendedStatus
        self.tags = tags
        self.fragment = fragment
        self.importance = importance
        self.previousStatus = previousStatus
        self.popularity = popularity # Loose proxy for word frequency
