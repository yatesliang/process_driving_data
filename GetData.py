import csv

class GetData:
    def __init__(self):
        pass
    def loadMetaData(self, path):
        with open(path, 'r', encoding='windows-1252') as csv_file:
            re = csv.DictReader(csv_file)
            reader = []
            for item in re:
                reader.append(item)
            result = []
            for i in range(len(reader)):
                item = reader[i]
                temp = {}
                temp["eventId"] = int(item["eventId"])
                # 行驶速度
                try:
                    temp["vX"] = float(item["FOT_Control.Speed"])
                except:
                    if reader[i+1]["FOT_Control.Speed"] != "NA":
                        temp["vX"] = (float(reader[i+1]["FOT_Control.Speed"]) + float(reader[i-1]["FOT_Control.Speed"]))/2
                        reader[i]["FOT_Control.Speed"] = temp["vX"]
                    else:
                        temp["vX"] = float(reader[i-1]["FOT_Control.Speed"])
                # 纵向加速度
                try:
                    temp["accY"] = float(item["IMU.Accel_Y"])
                except:
                    if reader[i+1]["IMU.Accel_Y"] != "NA":
                        temp["accY"] = (float(reader[i+1]["IMU.Accel_Y"]) + float(reader[i-1]["IMU.Accel_Y"]))/2
                        reader[i]["IMU.Accel_Y"] = temp["accY"]
                    else:
                        temp["accY"] = float(reader[i-1]["IMU.Accel_Y"])
                # 横向加速度
                try:
                    temp["accX"] = float(item["IMU.Accel_X"])
                except:
                    if reader[i+1]["IMU.Accel_X"] != "NA":
                        temp["accX"] = (float(reader[i+1]["IMU.Accel_X"]) + float(reader[i-1]["IMU.Accel_X"]))/2
                        reader[i]["IMU.Accel_X"] = temp["accX"]
                    else:
                        temp["accX"] = float(reader[i-1]["IMU.Accel_X"])
                # 时间戳
                temp["timeStamp"] = int(item["System.Time_Stamp"])
                # 与前车相对速度
                try:
                    temp["relativeSpeed"] = float(item["SMS.X_Velocity_T0"])
                except:
                    temp["relativeSpeed"] = 0

                # 与前车横向间距
                try:
                    temp["rangeX"] = float(item["SMS.X_Range_T0"])
                except:
                    temp["rangeX"] = 0

                # 与前车纵向间距
                try:
                    temp["rangeY"] = float(item["SMS.Y_Range_T0"])
                except:
                    temp["rangeY"] = 0
                # 前车ID
                try:
                    temp["frontId"] = int(item["SMS.Object_ID_T0"])
                except:
                    temp["frontId"] = -1
                # 车偏移车道的值
                try:
                    temp["laneOffset"] = float(item["Road.Scout.Lane_Offset"])
                except:
                    if reader[i+1]["Road.Scout.Lane_Offset"] != "NA":
                        temp["laneOffset"] = (float(reader[i+1]["Road.Scout.Lane_Offset"]) + float(reader[i-1]["Road.Scout.Lane_Offset"]))/2
                        reader[i]["Road.Scout.Lane_Offset"] = temp["laneOffset"]
                    else:
                        temp["laneOffset"] = float(reader[i-1]["Road.Scout.Lane_Offset"])
                result.append(temp)
            return result

    # 读取原始变道信息并返回一个list
    def getChangeLaneInfo(self, path):
        result = {}
        with open(path, 'r',encoding='windows-1252') as info:
            reader = csv.DictReader(info)
            for item in reader:
                result[item['eventId'] + '_start'] = int(item['changeFrom'])
                result[item['eventId']+'_point'] = int(item['changePoint'])
                result[item['eventId']] = int(item['driverId'])
        return result
    

