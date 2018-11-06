import numpy as np
from scipy import stats
import scipy.signal as signal
from process_data import open_csv as loadData
from process_data import get_change_lane_info as getInfo
from matplotlib import pyplot as plt
import time
# need:  event:a list contain 201 contents, each event item must contain frontId, timeStamp, laneOffset, range and frontSpeed(relative speed)
# 根据输入的event数据，输出开始/结束的时间点，输出前方车的相关数据：距离，相对速度
def getLaneChangeInfo(event, changPoint):
    pointIndex = 100
    startTime = 0
    frontId = []
    frontStart = -1
    frontEnd = -1
    startInfo = {}
    endInfo = {}
    endTime = 200
    threshold = 300                  # 30cm
    stdThreshold = 35
    # get the start time
    for i in range(100, 0, -1):
        # add the front car id into the list 
        startInfo['index'] = 50
        frontId.append((event[i])['frontId'])
        if abs((event[i])['laneOffset']) < threshold and startTime == 50:
            startTime = i
            startInfo['index'] = i
            startInfo['time'] = (event[i])['timeStamp']
        if i > 10:
            # calculate the std
            subList = []
            for j in range(i - 9, i+1):
                subList.append(event[j]['laneOffset'])
            std = np.std(subList)
            if std < stdThreshold:
                startTime = i
                startInfo['index'] = i
                startInfo['time'] = (event[i])['timeStamp']
                break

            
    frontStart = stats.mode(frontId)[0][0]
    # get the end time
    endInfo['index'] = 150
    for i in range(100,200,1):
        # add the front car id into the list 
        frontId.append((event[i])['frontId'])
        if abs((event[i])['laneOffset']) < threshold and endTime == 150:
            endTime = i
            endInfo['index'] = i
            endInfo['time'] = (event[i])['timeStamp']
        if i < 190:
            subList = []
            for j in range(i, i+10):
                subList.append(event[j]['laneOffset'])
            std = np.std(subList)
            if std < stdThreshold:
                endTime = i
                endInfo['index'] = i
                endInfo['time'] = (event[i])['timeStamp']
                break

    # Get the mode
    frontEnd = stats.mode(frontId)[0][0]
    # get the front car info
    if frontStart != -1:
        for i in range (startTime, pointIndex):
            item = event[i]
            if item['frontId'] == frontStart:
                startInfo['speed'] = item['relativeSpeed']
                startInfo['distance'] = item['rangeY']
                break
    else:
        startInfo['speed'] = 0
        startInfo['distance'] = 0

    if frontEnd != -1:
        for i in range (endTime, pointIndex, -1):
            item = event[i]
            if item['frontId'] == frontEnd:
                endInfo['speed'] = item['relativeSpeed']
                endInfo['distance'] = item['rangeY']
                break
    else:
        endInfo['speed'] = 0
        endInfo['distance'] = 0

    # eventInfo contain 'frontId', 'index', 'time', 'distance' and 'speed'
    return [startInfo,endInfo]
#
def preprocess(eventList):
    beforeChange = []
    afterChange = []
    # extract the lanOffset
    for i in range(0, len(eventList)):
        if i <= 95:
            beforeChange.append(eventList[i]['laneOffset'])
        if i >= 105:
            afterChange.append(eventList[i]['laneOffset'])
    # user medfilt to process the data
    beforeChange = signal.medfilt(beforeChange)
    afterChange = signal.medfilt(afterChange)
    for i in range(0, len(eventList)):
        if i <= 95:
            eventList[i]['laneOffset'] = beforeChange[i]
        if i >= 105:
            eventList[i]['laneOffset'] = afterChange[i-105]
    return eventList


# pass a list that contain 10 points
def calculateStd(subList):
    return()
    
def processById():
    # load data from csv file
    metaPath = "data/3batch_metaMotorway.csv"
    infoPath = "data/3batch_changeLane_eventInfo.csv"
    metaData = loadData(metaPath)
    infoData = getInfo(infoPath)
    eventLength = 201
    eventId = -1
    eventList = []
    eventInfo = {}
    events = []
    count = 0
    for item in metaData:
        if eventId == -1:
            eventId = item['eventId']
        if eventId != item['eventId']:
            if(len(eventList) == eventLength):
                print(eventId)
                print(item['eventId'])
                # pass the event list to get the start and end point and we can find the front car

                # preprocess the data

                eventList = preprocess(eventList)
                # implement a new method to calculate the start and end point
                info = getLaneChangeInfo(eventList, infoData[str(eventId)+'_point'])
                # Plot the figure here
                tempList = []
                for item1 in eventList:
                    tempList.append(item1['laneOffset'])
                

                fig = plt.figure(num=1, figsize=(15, 8), dpi=80)
                plt.plot(range(len(tempList)), tempList, color="red")
                plt.vlines(info[0]["index"], -3000, 3000, colors="green")
                plt.vlines(info[1]["index"], -3000, 3000, colors="green")
                plt.hlines(0, 0, 200, colors='yellow')
                plt.show()

                
                # Store the info here


                # Empty the eventList
            
                eventId = item['eventId']
                eventList = []
                eventList.append(item)
       
        else:
            eventList.append(item)
if __name__=="__main__":
     processById()