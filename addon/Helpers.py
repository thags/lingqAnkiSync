from datetime import datetime, timedelta

statusToInterval = {0: 0, 1: 5, 2: 10, 3: 20, 4: 40}


def convertAnkiIntervalToLingqStatus(interval) -> int:
    interval = int(interval)
    return next(
        (key for key, value in statusToInterval.items() if interval <= value),
        4,
    )


def convertLinqStatusToAnkiDueDate(linqStatus: int) -> str:
    return statusToInterval[linqStatus]
