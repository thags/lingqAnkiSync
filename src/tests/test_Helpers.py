from Helpers import Helpers

testIntervalConfig = {0: 0, 1: 5, 2: 10, 3: 20, 4: 40}

def test_should_Convert_Interval_To_Lingq_Status():
    helpers = Helpers(testIntervalConfig)
    lingqStatus = helpers.convertAnkiIntervalToLingqStatus(40)
    assert lingqStatus == 4
