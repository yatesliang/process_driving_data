import csv
import math

def open_csv(path):
    with open(path, 'r', encoding='windows-1252') as csv_file:
        reader = csv.DictReader(csv_file)
        result = []
        for item in reader:
            temp = {}
            temp["eventId"] = int(item["eventId"])
            temp["vX"] = float(item["FOT_Control.Speed"])
            temp["accY"] = float(item["IMU.Accel_Y"])
            temp["timeStamp"] = int(item["System.Time_Stamp"])
            temp["relativeSpeed"] = float(item["SMS.X_Velocity_T0"])
            temp["rangeX"] = float(item["SMS.X_Range_T0"])
            temp["rangeY"] = float(item["SMS.Y_Range_T0"])
            temp["frontId"] = int(item["SMS.Object_ID_T0"])
            temp["laneOffset"] = float(item["Road.Scout.Lane_Offset"])
            result.append(temp)
        return result


def calculate_speed(reader):
    result = {}
    id = 0
    for item in reader:
        if item['eventId'] != id:
            id = item['eventId']
            result[id] = 0
        if int(item["vX"]) * 3.6 >= 90.0:
            result[id] = result[id] + 1

    return result

def get_change_lane_info(path):
    result = {}
    with open(path, 'r',encoding='windows-1252') as info:
        reader = csv.DictReader(info)
        for item in reader:
            result[item['eventId'] + '_start'] = int(item['changeFrom'])
            result[item['eventId']+'_point'] = int(item['changePoint'])
            result[item['eventId']] = int(item['driverId'])
    return result

def calculate_speed_y(data, info):
    result = {}
    id = 0
    for item in data:
        if id != item['eventId']:
            id = item['eventId']
            result[item['eventId']] = 0
        if item['timeStamp'] > info[str(id) + '_start'] and item['timeStamp'] < info[str(id)+'_point'] - 1:
            result[id] = result[id] + item['accY'] * 0.1
    return result

def write_file(data, filename = "data.csv"):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for item in data:
            writer.writerow([item, data[item]])
    print("write file %s successfully" % filename)

def get_max_accY(data):
    result = {}
    id = 0
    for item in data:
        if id != item['eventId']:
            id = item['eventId']
            result[item['eventId']] = 0
        if abs(item['accY']) > result[id]:
            result[id] = item['accY']
    return result


def get_driver_id(data, info):
    result = data
    for item in result:
        result[item] = info[str(item)]
    return result

def get_speed_x(data, info):

    result = []
    id = 0
    temp_dic = {}
    for item in data:
        if id != item['eventId']:
            id = item['eventId']
            temp_dic['eventId'] = id
        if item['timeStamp'] == info[str(id) + '_start']:
            temp_dic['startSpeed'] = item['vX']
        if item['timeStamp'] == info[str(id)+'_point']:
            temp_dic['pointSpeed'] = item['vX']
            result.append(temp_dic)
            temp_dic = {}
    return result


def get_front_ttc(data, info):
    # if the relative speed is positive, return a negative value like -1
    result = []
    id = 0
    temp_dic = {}
    for item in data:
        if id != item['eventId']:
            id = item['eventId']
            temp_dic['eventId'] = id
        if item['timeStamp'] == info[str(id) + '_point']:
            if item['rangeX'] < 0 or abs(item['rangeY']) > 2.0:
                temp_dic['ttc'] = -1
            else:
                temp_dic['ttc'] = -item['rangeX'] / item['relativeSpeed']
            result.append(temp_dic)
            temp_dic = {}
    return result

def write_data_speed(data, filename):

    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['eventId', 'startSpeed', 'pointSpeed'])

        for item in data:
            writer.writerow([item['eventId'], item['startSpeed'], item['pointSpeed']])

    print("write file %s successfully" % filename)
def write_ttc(data, filename):

    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['eventId', 'ttc'])
        for item in data:
            writer.writerow([item['eventId'], item['ttc']])

    print("write file %s successfully" % filename)




if __name__ == "__main__":
    path_meta_data = "C:\\Users\\admin\\workspace\\3batchLaneChangeEvents\\3batch_metaMotorway.csv"
    path_info = "C:\\Users\\admin\\workspace\\3batchLaneChangeEvents\\3batch_changeLane_eventInfo.csv"
    data = open_csv(path_meta_data)
    info = get_change_lane_info(path_info)
    speed_over = calculate_speed(data)
    speed_y = calculate_speed_y(data, info)
    max_acc_y = get_max_accY(data)
    driver_info = get_driver_id(speed_y, info)
    speed_info = get_speed_x(data, info)
    ttc_info = get_front_ttc(data, info)
    # write_data_speed(speed_info, 'C:\\Users\\admin\\workspace\\3batchLaneChangeEvents\\driver_motor_speed_info.csv')
    # write_file(max_acc_y,  'C:\\Users\\admin\\workspace\\3batchLaneChangeEvents\\driver_motor_acc_y.csv')
    write_ttc(ttc_info,  'C:\\Users\\admin\\workspace\\3batchLaneChangeEvents\\driver_motor_ttc.csv')
    # write_file(speed_over, 'C:\\Users\\admin\\workspace\\3batchLaneChangeEvents\\speed_over_trunk.csv')
    # write_file(speed_y, 'C:\\Users\\admin\\workspace\\3batchLaneChangeEvents\\speed_y_trunk.csv')




