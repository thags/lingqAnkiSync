class Lingq:
    def __init__(self, primarykey, word, translation, status, extendedStatus=0):
        self.primaryKey = primarykey
        self.word = word
        self.translation = translation
        self.status = status
        self.extendedStatus = extendedStatus