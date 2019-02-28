import csv
import sys
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from  isodata_cluster import IsoData

'''sqlite3数据类型：INTEGER， REAL（浮点型），TEXT， BLOB
   "id","end","imei","links","org","start","track","vin"
'''

__table_name__ = 'yixin'
csv.field_size_limit(sys.maxsize)

class YixinTable(object) :
    def __init__(self):
        self._conn = sqlite3.connect('database.db')
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
        matrix = np.zeros((len(res), 4))
        for i in range(len(res)):
            lonlat = res[i][0].split(',')
            matrix[i,0] = float(lonlat[0])
            matrix[i,1] = float(lonlat[1])
            lonlat = res[i][1].split(',')
            matrix[i,2] = float(lonlat[0])
            matrix[i,3] = float(lonlat[1])
        return matrix

    def load(self, file):
        i = 0
        with open(file,"r",encoding="utf-8") as csvfile:
            point = csv.reader(csvfile)
            next(point)
            for en in point:
                print(i)
                i = i + 1
                self.insert(en[0].split('\"')[1], en[2], en[7], en[5], en[1], en[3], en[4], en[6])
                

yixin = YixinTable()
matrix = yixin.select('867012030288069') # 867012030288069/867012030289521
matrix = np.zeros((1, 4))
arr = np.array([1,2,3,4])
matrix[0,:] = [1,2,3,4]
matrix[0,0] = 1.0
matrix[0,1] = 2.0
matrix[0,2] = 3.0
matrix[0,3] = 4.0
data = [[0, 0], [1, 1], [2, 2], [4, 3], [5, 3], [4, 4], [5, 4], [6, 5]]
data1 = matrix[:,0:2].tolist()
print(matrix)
print(arr.dot(arr.T))
print(int(matrix.dot(matrix.T)))

# a.dot(a)
# data = matrix
# initial_set = [1, 20, 20, 20, 0.01, 1, 100, 0.5]
# isodata = IsoData(initial_set, data1)
# result = isodata.result

# for i in range(len(result)):
#     print('----------第' + str(i+1) + '个聚类----------')
#     print(result[i])

# fig = plt.figure()
# ax = fig.add_subplot(111)
# #设置标题  
# ax.set_title('start')
# #设置X轴标签  
# plt.xlabel('lon')  
# #设置Y轴标签  
# plt.ylabel('lat')
# #画散点图  
# ax.scatter(matrix[:,0], matrix[:,1] ,s = 1, c = 'r', marker = 'o')
# # ax.scatter(matrix[:,2], matrix[:,3] ,s = 1, c = 'b', marker = 'x')
# plt.show()
