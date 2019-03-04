import csv
import sys
import sqlite3
import numpy as np

'''sqlite3数据类型：INTEGER， REAL（浮点型），TEXT， BLOB
   "id","end","imei","links","org","start","track","vin"
'''

__table_name__ = 'yixin'
csv.field_size_limit(sys.maxsize)

class YixinTable(object) :
    def __init__(self):
        self._conn = sqlite3.connect('D:/sqlite3/yixin.db')
        self._cursor = self._conn.cursor()
        
        # self._cursor.execute('DROP TABLE ' + __table_name__) 
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + __table_name__ +
                             " ('id' TEXT PRIMARY KEY,'imei' TEXT NOT NULL, \
                              'vin' TEXT NOT NULL, 'start' TEXT, 'end' TEXT, 'links' TEXT, \
                              'org' TEXT, 'track' TEXT)",)

    def insert(self, nid, imei, vin, start, end, links, org, track):
        self._cursor.execute("INSERT INTO " + __table_name__ +
                               "('id', 'imei', 'vin', 'start', 'end', 'links', 'org', 'track')\
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (nid, imei, vin, start, end, links, org, track))
        self._conn.commit()
        
    def select(self, imei):
        self._cursor.execute("SELECT start, end from " + __table_name__ + ' where imei = \'' + imei + '\'')
        res = self._cursor.fetchall()
        matrix = []
        for i in range(len(res)):
            lonlat = res[i][0].split(',')
            matrix.append([float(lonlat[0]), float(lonlat[1])])
            # lonlat = res[i][1].split(',')
            # matrix[i,2] = float(lonlat[0])
            # matrix[i,3] = float(lonlat[1])
        return np.array(matrix)

    def load(self, file):
        i = 0
        with open(file,"r",encoding="utf-8") as csvfile:
            point = csv.reader(csvfile)
            next(point)
            for en in point:
                if len(en[3].split(',')) > 10:
                    print(i)
                    i = i + 1
                    self.insert(en[0].split('\"')[1], en[2], en[7], en[5], en[1], en[3], en[4], en[6])
