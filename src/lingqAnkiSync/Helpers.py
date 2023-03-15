#statusToInterval = {0: 0, 1: 5, 2: 10, 3: 20, 4: 40}

class Helpers:
    def __init__(self, statusToInverval=None):
        if statusToInverval is None:
            from .Config import Config
            self.config = Config()
            self.statusToInverval = self.config.getStatusToInterval()
        else:
            self.statusToInverval = statusToInverval
    
    def convertAnkiIntervalToLingqStatus(self, interval) -> int:
        interval = int(interval)
        return next(
            (key for key, value in self.statusToInverval.items() if interval <= value),
            4,
        )


    def convertLinqStatusToAnkiDueDate(self, linqStatus: int) -> str:
        return self.statusToInverval[linqStatus]
