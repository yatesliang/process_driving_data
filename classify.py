import csv
import numpy as np
import matplotlib.pyplot as plt

def loadFile(filePath):
    result = []
    with open(filePath, 'r') as csvFile:
        reader = csv.DictReader(csvFile)
        for item in reader:
            result.append(item)
    return result

def writeFile(filePath, data, header):
    with open(filePath, 'a') as csvFile:
        writer = csv.DictWriter(csvFile, header)
        writer.writeheader()
        writer.writerows(data)
    print("Write %s successfully" %filePath)


def grouped(data):
    currentId = 1
    lastEvent = {}
    currentEvent = {}
    newEventInfo = []
    temp = {}
    for i in range(len(data)):
        lastEvent = currentEvent
        currentEvent = data[i]
        if lastEvent:
            # 判断是同一个driver, 连续事件, 时间间隔 合适
            if  lastEvent['driverId'] == currentEvent['driverId'] and int(lastEvent['tag']) == 2 and int(currentEvent['tag']) == 2 and abs(int(currentEvent['startTime']) - int(lastEvent['endTime'])) < 15:
                temp['groupId'] = currentId
                temp['events'] = temp['events'] + 1
                temp['endTime'] = currentEvent['endTime']
                data[i]['groupId'] = currentId
            else:
                newEventInfo.append(temp)
                temp = {}
                currentId = currentId + 1
                data[i]['groupId'] = currentId
                temp['events'] = 1
                temp['groupId'] = currentId
                temp['startTime'] = currentEvent['startTime']
                temp['driverId'] = currentEvent['driverId']
                temp['endTime'] = currentEvent['endTime']
        else:
            data[i]['groupId'] = currentId
            temp['events'] = 1
            temp['groupId'] = currentId
            temp['driverId'] = currentEvent['driverId']
            temp['startTime'] = currentEvent['startTime']
            temp['endTime'] = currentEvent['endTime']
    print(newEventInfo)
    writeFile("newGroup.csv",newEventInfo, ["groupId", "startTime", "endTime", "events", "driverId"])
    header = ['eventId', 'duration', 'driverId', 'startTime', 'endTime', 'changePoint', 'averageSpeed', 'laneOffset', 'frontDistanceX', 'frontDistanceY', 'frontSpeed', 'tag', 'groupId']
    # writeFile("newInfoMotorway.csv", data, header)

def plotBox(data, speed):
    result = []
    labels = []
    temp = []
    for item in data:
        if float(item["averageSpeed"]) >= (speed/3.6):
            if (item["driverId"]) not in labels:
                if temp:
                    result.append(temp)
                temp = []
                labels.append((item["driverId"]))
            temp.append(float(item["duration"]))
    
    fig = plt.figure()
    ax = plt.subplot()
    # ax.set_xticks(labels)
    print(labels)
    ax.boxplot(result)
    ax.set_xticklabels(np.repeat(labels,1))
    
    plt.grid(axis='y')
    plt.show()



if __name__=="__main__":
    filePath = '/Users/LYC/Desktop/driving_style/Lane_Change/TrunkInfo.csv'
    data = loadFile(filePath)
    # grouped(data)
    plotBox(data, 70)
                

        