class Lingq:
    LEVEL_1 = 'new'
    LEVEL_2 = 'recognized'
    LEVEL_3 = 'familiar'
    LEVEL_4 = 'learned'
    LEVEL_KNOWN = 'known'
    LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_KNOWN]

    def __init__(self, primarykey, word, translations, status, extended_status, tags, fragment, importance, popularity = 0):
        self.primaryKey = primarykey
        self.word = word
        self.translations = translations
        self.status = status
        self.extended_status = extended_status
        self.tags = tags
        self.fragment = fragment
        self.importance = importance
        self.popularity = popularity # Loose proxy for word frequency
