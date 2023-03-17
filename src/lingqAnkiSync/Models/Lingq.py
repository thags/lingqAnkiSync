class Lingq:
    def __init__(self, primarykey, word, translation, status, extendedStatus):
        self.primaryKey = primarykey
        self.word = word
        self.translation = translation
        self.status = None
        self.extended_status = None
        self.SetStatus(status, extendedStatus)
        
    def SetStatus(self, status, extended_status):
        if (extended_status is None): extended_status = 0
        if (status is None): status = 0
        if (status == 3 and extended_status == 3):
            self.extended_status = 3
            self.status = 3
        else:
            self.status = status
            self.extended_status = 0
            
    def SetStatusForExport(self):
        if (self.status <= 0): 
            self.status = 0
            self.extended_status = 0
        if (self.status >= 4):
            self.status = 3
            self.extended_status = 3
        else:
            self.extended_status = 0