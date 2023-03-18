import sys, os
sys.path.append(
    os.path.realpath(f"{os.path.dirname(__file__)}/../LingqAnkiSync")
)
from Converter import _ConvertAnkiIntervalToLingqStatus, _ConvertLingqStatusToAnkiInterval


def test_ConvertAnkiIntervalToLingqStatus():
    #arrange
    testStatusToInterval = {0:100, 1:200, 2:300, 3:400, 4:500}
    testInterval = 225
    #act
    resultStatus = _ConvertAnkiIntervalToLingqStatus(testInterval, testStatusToInterval)
    #assert
    assert resultStatus == 2
