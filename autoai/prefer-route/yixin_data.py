import csv
import sys
import sqlite3
import numpy as np
import pymongo as pm
import logging


'''
   sqlite3数据类型：INTEGER， REAL（浮点型），TEXT， BLOB
   "id","end","imei","links","org","start","track","vin"
   从mongo库倒数据到本地sqlite
'''
__table_name__ = 'yixin_org'
__table_name_filte__ = 'yixin_org_filte'
__yixin_experience_org__ = 'yixin_experience_org'
__mongo_host__ = '192.168.145.79'
__mongo_port__ = 27017

__LOG_FORMAT__ = "%(asctime)s - %(levelname)s - %(message)s"
__DATE_FORMAT__ = "%m-%d-%Y %H:%M:%S %p"

logging.basicConfig(level=logging.INFO, filename='my.log', datefmt=__DATE_FORMAT__, format=__LOG_FORMAT__)   #从debug输出

class YixinData(object):
    def __init__(self, data):
        self.id = data[0]
        self.imei = data[1]
        self.vin = data[2]
        self.start = data[3]
        self.end = data[4]
        self.startTime = data[5]
        self.endTime = data[6]
        self.runTime = data[7]
        self.interval = data[8]
        self.speed = data[9]
        self.startMean = data[10]
        self.endMean = data[11]
        self.org = data[12]

class YixinTable(object) :
    def __init__(self):
        # /mapbar/data/sqlite3
        self._conn = sqlite3.connect('D:/sqlite3/yixin.db')
        # self._conn = sqlite3.connect('/mapbar/data/sqlite3/yixin.db')
        self._cursor = self._conn.cursor()
        
        # self._cursor.execute('DROP TABLE ' + __table_name__) 
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + __table_name__ + " ('id' TEXT PRIMARY KEY,'imei' TEXT NOT NULL, 'vin' TEXT NOT NULL,  \
                                 'start' TEXT, 'end' TEXT, 'startTime' INTEGER, 'endTime' INTEGER, 'runTime' INTEGER, \
                                     'interval' REAL, 'speed' REAL, 'startMean' TEXT, 'endMean' TEXT, 'org' TEXT)")
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + __table_name_filte__ + " ('id' TEXT PRIMARY KEY,'imei' TEXT NOT NULL, 'vin' TEXT NOT NULL, \
                                 'start' TEXT, 'end' TEXT, 'startTime' INTEGER, 'endTime' INTEGER, 'runTime' INTEGER, \
                                     'interval' REAL, 'speed' REAL, 'startMean' TEXT, 'endMean' TEXT, 'org' TEXT)")
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + __yixin_experience_org__ + " ('imei' TEXT NOT NULL, \
                                'vin' TEXT NOT NULL, 'startMean' TEXT, 'endMean' TEXT, 'startTime' INTEGER, 'yixin_ids' TEXT, 'correct_id' TEXT, 'org' TEXT)")

    def insert_experience_org(self, imei, vin, startMean, endMean, startTime, yixin_ids, correct_id, org):
        self._cursor.execute("INSERT INTO "  + __yixin_experience_org__ + " ('imei', 'vin', 'startMean', 'endMean', 'startTime', 'yixin_ids', 'correct_id', \
                            'org') VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (imei, vin, startMean, endMean, startTime, yixin_ids, correct_id, org))

    def insert(self, id, imei, vin, start, end, startTime, endTime, runTime, interval, speed, startMean, endMean, org):
        self._cursor.execute("INSERT INTO "  + __table_name__ + " ('id', 'imei', 'vin', 'start', 'end', 'startTime', 'endTime', 'runTime', \
                            'interval', 'speed', 'startMean', 'endMean', 'org') VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)",
                                (id, imei, vin, start, end, startTime, endTime, runTime, interval, speed, startMean, endMean, org))
        if interval > 5:
            self._cursor.execute("INSERT INTO "  + __table_name_filte__ + " ('id', 'imei', 'vin', 'start', 'end', 'startTime', 'endTime', 'runTime', \
                            'interval', 'speed', 'startMean', 'endMean', 'org') VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)",
                                (id, imei, vin, start, end, startTime, endTime, runTime, interval, speed, startMean, endMean, org))
    
    def update(self, id, startMean, endMean):
        self._cursor.execute("update %s set startMean = \'%s\', endMean = \'%s\' where id = \'%s\'" % (__table_name_filte__, startMean, endMean, id))
        
    def commit(self):
        self._conn.commit()

    # def select(self, imei):
    #     self._cursor.execute("SELECT * from " + __table_name_filte__ + ' where imei = \'' + imei + '\'')
    #     res = self._cursor.fetchall()

    def select(self, imei):
        # self._cursor.execute("SELECT id, start, end from " + __table_name_filte__ + ' where imei = \'' + imei + '\'s')
        self._cursor.execute("SELECT * from %s where imei = \'%s\'" % (__table_name_filte__, imei))
        res = self._cursor.fetchall()
        dict = {}
        for i in range(len(res)):
            yixin_data = YixinData(res[i])
            dict[yixin_data.id] = yixin_data
        return dict

    def up_mongo(self):
        client = pm.MongoClient(__mongo_host__, __mongo_port__)  # 端口号是数值型
        db = client['location-platform']
        stb = db[__yixin_experience_org__]
        res = self._cursor.execute("SELECT * from %s" % __yixin_experience_org__)
        # res = self._cursor.fetchall()
        k = 0
        for en in res:
            dict = {}
            dict['imei'] = en[0]
            dict['vin'] = en[1]
            dict['startMean'] = en[2]
            dict['endMean'] = en[3]
            dict['startTime'] = en[4]
            dict['yixin_ids'] = en[5]
            dict['correct_id'] = en[6]
            dict['org'] = en[7]
            stb.insert_one(dict)
            k += 1
            print(k)
    def load(self, imei):
        # 获取连接
        client = pm.MongoClient(__mongo_host__, __mongo_port__)  # 端口号是数值型
        # 连接数据库location-platform
        db = client['location-platform']
        # 获取集合
        stb1 = db.PartSplit
        stb2 = db.t_yixin_org_data

        # 获取数据信息  
        datas = stb1.find({'imei':imei},{"extend":0,"parts":0,"points":0,"_class":0})
        k = 0
        for en in datas:
            org = stb2.find_one({'_id':str(en['_id']) + "#" + en['imei']}, {"orgLonlats":1})
            if org != None and org['orgLonlats'] != '':
                org = org['orgLonlats']
                k += 1
                self.insert(str(en['_id']), en['imei'], en['vin'], str(en['startLon']) + ',' + str(en['startLat']), str(en['endLon']) + ',' + str(en['endLat']), 
                        en['startTime'], en['endTime'], en['runTime'], en['interval'], en['speed'], '', '', org)
        logging.debug('%s 包含的轨迹条数：%s' % (imei, k))
        self._conn.commit()
            
if __name__ == "__main__":
    yixin = YixinTable()
    # yixin.load('867012030287491') # 867012030302811  "867012030287491"
    yixin.up_mongo()
