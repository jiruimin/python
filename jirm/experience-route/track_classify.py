'''
对单个用户的行驶轨迹按聚合后的起终点进行分类
'''

import sqlite3
from yixin_data import YixinTable
import math

__yixin = YixinTable()

''' 
对一个imei所有的 通信距离大于5公里的经纬度串
'''
def classify(imei):
    res_dict = {}
    yixin_dict = __yixin.select(imei)
    for value in yixin_dict.values():
        if ',' in value.startMean and ',' in value.endMean:
            lonlat = value.startMean.split(',')
            start_lon = float(lonlat[0])
            start_lat = float(lonlat[1])
            lonlat = value.endMean.split(',')
            end_lon =  float(lonlat[0])
            end_lat = float(lonlat[1])
            # 起点和终点距离在5公里内，则不予考虑
            if math.sqrt(pow(end_lon - start_lon, 2) + pow(end_lat - start_lat, 2)) > 0.05:
                key = value.startMean + ';' + value.endMean
                if key in res_dict.keys():
                    res_dict[key].append(value)
                else:
                    res_dict[key] = [value]
    return res_dict

'''
计算经纬度串通过的网格号
'''
def get_grid(lonlats):
    res_set = set()
    lonlats = lonlats.split(';')
    for lonlat in lonlats:
        lonlat = lonlat.split(',')
        lon = int(float(lonlat[0]) / 0.00015)
        lat = int(float(lonlat[1]) / 0.00015)
        res_set.add(str(lon) + '#' + str(lat))
    return res_set

'''
计算一串经纬度里面通行频率最高的一条路线
'''
def get_experience_lonlat(lonlats_list):
    grade = []
    lonlat_grid_set = []
    total_grid = {}
    for lonlats in lonlats_list:
        grid_set = get_grid(lonlats)
        lonlat_grid_set.append(grid_set)
        for grid in grid_set:
            if grid in total_grid:
                total_grid[grid] += 1
            else:
                total_grid[grid] = 1
    
    for lonlat_grid in lonlat_grid_set:
        g = 0
        for grid in lonlat_grid:
            g += total_grid[grid]
        grade.append(g)
    
    res = 0
    index = 0
    for i in range(len(grade)):
        if grade[i] > res:
            res = grade[i]
            index = i
    return index


if __name__ == "__main__":
    yixin_dict = classify(867012030302811)   # 867012030287491  "867012030287491"
    for key,value in yixin_dict.items():
        lonlats_list = []
        yixin_ids = []
        for data in value:
            lonlats_list.append(data.org)
            yixin_ids.append(data.id)
        index = get_experience_lonlat(lonlats_list)
        __yixin.insert_experience_org(value[0].imei, value[0].vin,  value[0].startMean,  value[0].endMean,
                 value[0].startTime, str(yixin_ids), yixin_ids[index], lonlats_list[index])
    __yixin.commit()