from GetData import GetData
from calculate_ttc import processById

dataPath = "data/3batch_metaMotorway.csv"
infoPath = "data/3batch_changeLane_eventInfo.csv"
dataGet = GetData()
metaData = dataGet.loadMetaData(dataPath)
infoData = dataGet.getChangeLaneInfo(infoPath)
processById(metaData, infoData, "test/info2.csv", "test/images/")