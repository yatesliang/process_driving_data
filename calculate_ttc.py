import numpy as np
from scipy import stats
import scipy.signal as signal
from process_data import open_csv as loadData
from process_data import get_change_lane_info as getInfo
from matplotlib import pyplot as plt
import time
import csv
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
    tag = 1                        # 1 means it is a single lane change event and 2 represent the continues
    endTime = 200
    threshold = 300                  # 30cm
    stdThreshold = 35
    # get the start time
    zeropoint = False
    startInfo['index'] = 50
   
    for i in range(95, 0, -1):
        # add the front car id into the list 
        
        frontId.append((event[i])['frontId'])
        if abs((event[i])['laneOffset']) > 800 and zeropoint:
            tag = 2
            # print("mutil-events-frot")
            break
        if (event[i])['laneOffset'] * (event[i + 1])['laneOffset'] < 1 and not zeropoint:
            # print((event[i])['laneOffset'])
            # print(zeropoint)
            startTime = i
            zeropoint = True
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
        startInfo['time'] = (event[startTime])['timeStamp']
            
    frontStart = stats.mode(frontId)[0][0]
    frontId = []
    # get the end time
    zeropoint = False
    endInfo['index'] = 150
    
    for i in range(105,200,1):
        # add the front car id into the list 
        
        frontId.append((event[i])['frontId'])
        if (event[i])['laneOffset'] * (event[i - 1])['laneOffset'] < 1 and not zeropoint:
            zeropoint = True
            endTime = i
            endInfo['index'] = i
            endInfo['time'] = (event[i])['timeStamp']
        if abs((event[i])['laneOffset']) > 800 and zeropoint:
            tag = 2
            # print('multi-events-end')
            break
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
    endInfo['time'] = (event[endTime])['timeStamp']
    # Get the mode
    frontEnd = stats.mode(frontId)[0][0]
    # get the front car info
    startInfo['speed'] = 0
    startInfo['distanceX'] = 0
    startInfo['distanceY'] = 0
    if frontStart != -1:
        for i in range (startTime, pointIndex):
            item = event[i]
            if item['frontId'] == frontStart and item['relativeSpeed'] > 0.05:
                startInfo['speed'] = item['relativeSpeed']
                startInfo['distanceX'] = item['rangeX']
                startInfo['distanceY'] = item['rangeY']
                break

    endInfo['speed'] = 0
    endInfo['distanceX'] = 0
    endInfo['distanceY'] = 0
    if frontEnd != -1:
        for i in range (endTime, pointIndex, -1):
            item = event[i]
            if item['frontId'] == frontEnd and item['relativeSpeed'] > 0.05:
                endInfo['speed'] = item['relativeSpeed']
                endInfo['distanceX'] = item['rangeX']
                endInfo['distanceY'] = item['rangeY']
                break

    startInfo['eventId'] = event[pointIndex]['eventId']
    endInfo['eventId'] = event[pointIndex]['eventId']
    startInfo['tag'] = endInfo['tag'] = tag
    startInfo['laneOffset'] = event[startInfo['index']]['laneOffset']
    endInfo['laneOffset'] = event[endInfo['index']]['laneOffset']
    

    # eventInfo contain 'frontId', 'index', 'time', 'distance' and 'speed', 'laneOffset', 'tag', 'eventId'
    return [startInfo,endInfo]
# 中值滤波平滑曲线
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



    
def processById(metaData, infoData, infoSavePath, imageSavePath):
    # load data from csv file
    infos = []
    eventLength = 201
    eventId = -1
    eventList = []
    eventInfo = {}
    events = []
    count = 0
    for item in metaData:
        count = count + 1
        print("进度:{0}%".format(round(count * 100 / len(metaData))), end="\r")
        if eventId == -1:
            eventId = item['eventId']
        if eventId != item['eventId']:
            if(len(eventList) == eventLength):
                # print(item['eventId'])
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
                plt.vlines(info[0]["index"], -3000, 3000, linestyles="--", colors="blue")
                plt.vlines(info[1]["index"], -3000, 3000, linestyles="--", colors="blue")
                plt.xlabel("Time")
                plt.ylabel("LaneOffset")
                plt.title("Event_%s"%eventId)
                plt.hlines(0, 0, 200, linestyles="--", colors='green')
                plt.legend(["laneoffset", 'start', 'end' , 'zero'])
                # save images
                plt.savefig(imageSavePath+'event_'+str(eventId))
                plt.close()
                # plt.show()
                

                
                # Store the info here
                tempDic = {}
                tempDic['eventId'] = eventId
                tempDic['duration'] = (info[1]['index'] - info[0]['index'])/ 10.0  # (s)
                # print(info[0]['index'])
                # print(info[1]['index'])
                # print(tempDic['duration'])
                tempDic['driverId'] = infoData[str(eventId)]
                tempDic['tag'] = info[0]['tag']
                tempDic['startTime'] = info[0]['time']
                tempDic['endTime'] = info[1]['time']
                tempDic['changePoint'] = infoData[str(eventId)+'_point']
                tempDic['laneOffset'] = info[1]['laneOffset']
                tempDic['averageSpeed'] = averageSpeed(info[0]['index'], info[1]['index'], eventList)
                # TODO:Average PAccX PAccY NAccX NAccY
                [tempDic['pAccX'], tempDic['nAccX'], tempDic['pAccY'], tempDic['nAccY']] = accInfo(info[0]['index'], info[1]['index'], eventList)
                # TODO: Get Peak Acc
                [tempDic['maxAccX'], tempDic['minAccX'], tempDic['maxAccY'], tempDic['minAccY']] = getMaxAcc(info[0]['index'], info[1]['index'], eventList)
                # TODO: Get Point Acc
                tempDic['pointAccX'] = eventList[100]['accX']
                tempDic['pointAccY'] = eventList[100]['accY']
                tempDic['pointSpeed'] = eventList[100]['vX']

                tempDic['frontDistanceX'] = info[0]['distanceX']
                tempDic['frontDistanceY'] = info[0]['distanceY']
                tempDic['frontSpeed'] = info[0]['speed']
                infos.append(tempDic)

                # Empty the eventList
            
                eventId = item['eventId']
                eventList = []
                eventList.append(item)
       
        else:
            eventList.append(item)
    # store all info to file
    writeToFile(infoSavePath, infos)

# TODO:Calculate average acc
def accInfo(startIndex, endIndex, eventList):
    endIndex = endIndex + 1
    pAccX = 0
    pXCount = 0
    nAccX = 0
    nXCount = 0
    pAccY = 0
    pYCount = 0
    nAccY = 0
    nYCount = 0
    for i in range(startIndex, endIndex):
        accX = eventList[i]["accX"]
        accY = eventList[i]["accY"]
        if  accX < 0:
            nAccX  = nAccX + accX
            nXCount = nXCount + 1
        else:
            pAccX = pAccX + accX
            pXCount = pXCount + 1
        if accY < 0:
            nAccY = nAccY +  accY
            nYCount = nYCount + 1
        else:
            pAccY = pAccY + accY
            pYCount = pYCount + 1
    if pXCount == 0:
        pXCount = 1
    if pYCount == 0:
        pYCount = 1
    if nXCount == 0:
        nXCount = 1
    if nYCount == 0:
        nYCount = 1
    pAccX = pAccX/pXCount
    nAccX = nAccX/nXCount
    pAccY = pAccY/pYCount
    nAccY = nAccY/nYCount
    return [pAccX, nAccX, pAccY, nAccY]

# TODO:Get peak acc

def getMaxAcc(startIndex, endIndex, eventList):
    endIndex = endIndex + 1
    maxAccX = -1
    minAccX = 1
    maxAccY = -1
    minAccY = 1
    for i in range (startIndex, endIndex):
        accX = eventList[i]["accX"]
        accY = eventList[i]["accY"]
        if accX > maxAccX:
            maxAccX = accX
        if accX < minAccX:
            minAccX = accX
        if accY > maxAccY:
            maxAccY = accY
        if accY < minAccY:
            minAccY = accY
    return [maxAccX, minAccX, maxAccY, minAccY]



# Extract start and end index from the first two parameters and calculate the average speed of the event
def averageSpeed(startIndex, endIndex, eventList):
    endIndex = endIndex + 1
    speed = 0.0
    for i in range(startIndex, endIndex):
        speed += eventList[i]["vX"]
    return speed/(endIndex-startIndex)

def writeToFile(filename, file):
    header = ['eventId', 'duration', 'driverId', 'startTime', 'endTime', 'changePoint', 'averageSpeed', 'laneOffset', 'frontDistanceX', 'frontDistanceY', 'frontSpeed', 'tag']
    header = header + ['pAccX', 'nAccX', 'pAccY', 'nAccY', 'maxAccX', 'minAccX', 'maxAccY', 'minAccY', 'pointAccX', 'pointAccY', 'pointSpeed']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, header)
        writer.writeheader()
        for item in file:
            writer.writerow(item)
    print("Store Info in %s Done"%filename)



if __name__=="__main__":
     pass