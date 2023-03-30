class AnkiCard:
    def __init__(self, primarykey, word, translations, interval, status, extended_status, tags, sentence, importance):
        self.primaryKey = primarykey
        self.word = word
        self.translations = translations
        self.interval = interval
        self.status = status
        self.extended_status = extended_status
        self.tags = tags
        self.sentence = sentence
        self.importance = importance