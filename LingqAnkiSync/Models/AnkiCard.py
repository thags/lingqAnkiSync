class AnkiCard:
    def __init__(
        self,
        primary_key,
        word,
        translations,
        interval,
        status,
        tags,
        sentence,
        importance,
        popularity=0,
    ):
        self.primary_key = primary_key
        self.word = word
        self.translations = translations
        self.interval = interval
        self.status = status
        self.tags = tags
        self.sentence = sentence
        self.importance = importance
        self.popularity = popularity
