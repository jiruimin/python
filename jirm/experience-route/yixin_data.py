import csv
import sys
import sqlite3
import numpy as np
import pymongo as pm

'''sqlite3数据类型：INTEGER， REAL（浮点型），TEXT， BLOB
   "id","end","imei","links","org","start","track","vin"

   从mongo库倒数据到本地sqlite
'''

__table_name__ = 'yixin_org'
__table_name_filte__ = 'yixin_org_filte'
__mongo_host__ = '192.168.145.79'
__mongo_port__ = 27017

class YixinTable(object) :
    def __init__(self):
        self._conn = sqlite3.connect('D:/sqlite3/yixin.db')
        self._cursor = self._conn.cursor()
        
        # self._cursor.execute('DROP TABLE ' + __table_name__) 
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + __table_name__ + " ('id' TEXT PRIMARY KEY,'imei' TEXT NOT NULL, 'vin' TEXT NOT NULL, \
                                 'start' TEXT, 'end' TEXT, 'startTime' INTEGER, 'endTime' INTEGER, 'runTime' INTEGER, \
                                     'interval' REAL, 'speed' REAL, 'startMean' TEXT, 'endMean' TEXT, 'org' TEXT)")
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + __table_name_filte__ + " ('id' TEXT PRIMARY KEY,'imei' TEXT NOT NULL, 'vin' TEXT NOT NULL, \
                                 'start' TEXT, 'end' TEXT, 'startTime' INTEGER, 'endTime' INTEGER, 'runTime' INTEGER, \
                                     'interval' REAL, 'speed' REAL, 'startMean' TEXT, 'endMean' TEXT, 'org' TEXT)")

    def insert(self, id, imei, vin, start, end, startTime, endTime, runTime, interval, speed, org, startMean='', endMean=''):
        self._cursor.execute("INSERT INTO "  + __table_name__ + " ('id', 'imei', 'vin', 'start', 'end', 'startTime', 'endTime', 'runTime', \
                            'interval', 'speed', 'startMean', 'endMean', 'org') VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)",
                                (id, imei, vin, start, end, startTime, endTime, runTime, interval, speed, org, startMean, endMean))
        if interval > 5:
            self._cursor.execute("INSERT INTO "  + __table_name_filte__ + " ('id', 'imei', 'vin', 'start', 'end', 'startTime', 'endTime', 'runTime', \
                            'interval', 'speed', 'startMean', 'endMean', 'org') VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)",
                                (id, imei, vin, start, end, startTime, endTime, runTime, interval, speed, org, startMean, endMean))
    
    def update(self, id, startMean, endMean):
        self._cursor.execute("update " + __table_name_filte__ +" set startMean = \'%s\', endMean = \'%s\' where id = \'%s\'" % (startMean, endMean, id))
        
    def commit(self):
        self._conn.commit()

    def select(self, imei):
        self._cursor.execute("SELECT id, start, end from " + __table_name_filte__ + ' where imei = \'' + imei + '\'')
        res = self._cursor.fetchall()
        dict = {}
        start_matrix, end_matrix  = [], []
        for i in range(len(res)):
            dict[res[i][0]] = (res[i][1], res[i][2])

            lonlat = res[i][1].split(',')
            start_matrix.append([float(lonlat[0]), float(lonlat[1])])

            lonlat = res[i][2].split(',')
            end_matrix.append([float(lonlat[0]), float(lonlat[1])])
        return start_matrix, end_matrix, dict

    def load(self):
        # 获取连接
        client = pm.MongoClient(__mongo_host__, __mongo_port__)  # 端口号是数值型
        # 连接数据库location-platform
        db = client['location-platform']
        # 获取集合
        stb1 = db.PartSplit
        stb2 = db.t_yixin_org_data

        # 获取数据信息   867012030302811  "867012030287491"
        datas = stb1.find({'imei':'867012030302811'},{"extend":0,"parts":0,"points":0,"_class":0})
        k = 0
        for en in datas:
            org = stb2.find_one({'_id':str(en['_id']) + "#" + en['imei']}, {"orgLonlats":1})
            if org != None and org['orgLonlats'] != '':
                org = org['orgLonlats']
                k += 1
                print(k)
                self.insert(str(en['_id']), en['imei'], en['vin'], str(en['startLon']) + ',' + str(en['startLat']), str(en['endLon']) + ',' + str(en['endLat']), 
                        en['startTime'], en['endTime'], en['runTime'], en['interval'], en['speed'], '', '', org)
        self._conn.commit()
            
if __name__ == "__main__":
    yixin = YixinTable()
    yixin.load()
    print(yixin.select('867012030302811'))
