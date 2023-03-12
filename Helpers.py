from datetime import datetime

statusToInterval = {0: 1, 1: 5, 2: 10, 3: 15, 4: 30}

def convertAnkiDueDateToLingqStatus(dueDateUnFormated: str) -> int:
    dueDate = datetime.strptime(dueDateUnFormated, '%Y-%m-%d').date()
    today = datetime.today().date()
    interval = (dueDate - today).days
    if interval < 0:
        return 0
    for key, value in statusToInterval.items():
        if interval <= value:
            return key
    return 5

def convertLinqStatusToAnkiDueDate(linqStatus: int) -> int:
    return statusToInterval[linqStatus]