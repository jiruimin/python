'''
isodata聚合算法实现，基于numpy库

# initial_set为初始设置，依次代表如下：
# nc : 预选nc个聚类中心
# K：希望的聚类中心个数
# min_num：每个聚类中最少样本数
# s：聚类域中样本的标准差阈值
# c：两聚类中心之间的最短距离
# L：在一次迭代中允许合并的聚类中心的最大对数
# I：允许迭代的次数
# k：分裂系数
'''

import numpy as np
from yixin_data import YixinTable 
import matplotlib.pyplot as plt
import logging

__LOG_FORMAT__ = "%(asctime)s - %(levelname)s - %(message)s"
__DATE_FORMAT__ = "%m-%d-%Y %H:%M:%S %p"

logging.basicConfig(level=logging.INFO,datefmt=__DATE_FORMAT__,format=__LOG_FORMAT__)   #从debug输出

class IsoData(object):

    def __init__(self, initial_set, data):
        self.flag = True

        # initial_set 为初始设置集合，依次为nc,K,min_num,s,c,L,I,k
        self.nc = initial_set[0]
        self.K = initial_set[1]
        self.min_num = initial_set[2]
        self.s = initial_set[3]
        self.c = initial_set[4]
        self.L = initial_set[5]
        self.I = initial_set[6]
        self.k = initial_set[7]

        self.current_i = 0  # 目前迭代的次数
        self.data = np.array(data)    # 数据集
        self.outlier = []  # 离群数据集

        self.center = []  # 聚类中心list
        self.result = []  # 聚类结果
        self.inner_mean_distance = []  # 类内平均距离

        self.all_mean_distance = 0  # 全部样本的总体平均距离
        # 预选nc个聚类中心
        for i in range(self.nc):
            d = self.data[int(len(self.data) * i / self.nc)]
            self.center.append(d)
    
    def get_result(self):
        dict = {}
        for i in range(len(self.center)):
            ll = ''
            for j in range(len(self.result[i])):
                # dict[str(self.result[i][j][0]) + ',' + str(self.result[i][j][1])] = str(self.center[i][0]) + ',' + str(self.center[i][1])
                point = str(self.result[i][j][0]) + ',' + str(self.result[i][j][1])
                dict[point] = '%.5f,%.5f' % (self.center[i][0], self.center[i][1])
                ll += (point + ';')
            logging.debug('%s/%s:%5f,%5f------%s' % (len(self.center), i, self.center[i][0], self.center[i][1], ll))
        return dict

    def start(self):
        if not self.flag:
            return
        self.current_i += 1
        logging.debug('第[%s]轮循环......当前中心点[%s]：' % (len(self.center), self.current_i), str(self.center), sep='')
        
        # 将全体样本分类
        if self.current_i == 1:
            result = [self.data]
        else:
            result = self.result.copy()  # 聚类结果
        self.result = self.center.copy()
        # for i in range(self.data.shape[0]):
        for i in range(len(result)):
            for k in range(len(result[i])):
                point = result[i][k]
                index = 0
                dis_min = 9999
                for j in range(len(self.center)):
                    dis_l = np.linalg.norm(self.center[j] - point)
                    if dis_l < dis_min:
                        dis_min = dis_l
                        index = j
                self.result[index] = np.vstack((self.result[index], point)) 
        # 删除第一个点，第一个点为类中心点，删除重复添加
        for i in range(len(self.result)):
            if self.result[i].shape == (2,):
                self.result[i] = []
            else:
                self.result[i] = np.delete(self.result[i], 0, axis = 0)

        # self.show()
        # 删除样本条数小于min_num的分类
        for i in range(len(self.result) - 1, -1, -1):
            if len(self.result[i]) <= self.min_num:
                self.outlier.append(self.result[i])
                self.result.pop(i)
                self.center.pop(i)
                self.nc -= 1
        self.step4_5_6()

    # 调整各类型中心点 + 计算类内平均距离 + 计算总体平均距离
    def step4_5_6(self):
        # 调整各类型中心点 + 计算类内平均距离
        self.inner_mean_distance = []
        self.center = []  # 聚类中心list
        for i in range(len(self.result)):
            sum_1 = np.mean(self.result[i], axis=0)
            inner_all_distance = 0
            for j in range(len(self.result[i])):
                inner_all_distance += np.linalg.norm(self.result[i][j] - sum_1)
            self.inner_mean_distance.append(inner_all_distance / len(self.result[i]))
            self.center.append(sum_1)

        # 计算总体平均距离
        all_mean_distance = 0
        all_mean_distance_num = 0
        for i in range(len(self.inner_mean_distance)):
            all_mean_distance += (self.inner_mean_distance[i] * self.result[i].shape[0])
            all_mean_distance_num += self.result[i].shape[0]
        self.all_mean_distance = all_mean_distance / all_mean_distance_num
        self.step7()

    # 判断是否迭代，进行分裂还是合并
    def step7(self):
        if(self.current_i >= self.I):
            return self.center, self.result
        # self.show()
        # 迭代次数超过设置值 or 迭代次数是偶数次 or 分类数大于2K
        if self.current_i > self.I or self.current_i % 2 == 0 or self.nc >= 2 * self.K:
            # 合并
            self.step11()
        else:
            # 分裂
            self.step8_9_10()

    def step8_9_10(self):
        # 计算每类样本群的标准差向量
        logging.debug('第[%s]轮循环......分裂' % self.current_i)
        max_standard_index = []
        max_standard_dev = []
        for i in range(len(self.result)):
            std_vec = np.std(self.result[i], axis=0)
            index = np.argmax(std_vec)
            max_standard_index.append(index)
            max_standard_dev.append(std_vec[index])

        flag = False
        
        for i in range(len(max_standard_dev) - 1, -1, -1):
            if max_standard_dev[i] > self.s and \
                    ((self.result[i].shape[0] > 2 * self.min_num) or self.nc < self.K / 2):
                    # ((self.inner_mean_distance[i] > self.all_mean_distance and self.result[i].shape[0] > 2 * self.min_num) or self.nc < self.K / 2):
                # 分裂操作
                self.nc += 1
                center = self.center[i]
                self.center.pop(i)
                new_center1, new_center2 = center.copy(), center.copy()
                new_center1[max_standard_index[i]] = new_center1[max_standard_index[i]] - self.k * max_standard_dev[i]
                new_center2[max_standard_index[i]] = new_center2[max_standard_index[i]] + self.k * max_standard_dev[i]
                self.center.append(new_center1)
                self.center.append(new_center2)
                flag = True
        if(flag):
            self.start()
        else:
            self.step11()

    # 合并操作
    def step11(self):
        logging.debug('第[%s]轮循环......合并' % self.current_i)
        dis_center = 999
        for i in range(len(self.center)):
            for j in range(i + 1, len(self.center)):
                dis_l = np.linalg.norm(self.center[i] - self.center[j])
                if dis_l < dis_center:
                    min_center = (i, j)
                    dis_center = dis_l
        
        
        if dis_center < self.c:
            i = min_center[0]
            j = min_center[1]
            center_new = (self.center[i] * self.result[i].shape[0] + self.center[j] * self.result[j].shape[0]) / (self.result[i].shape[0] + self.result[j].shape[0])
            self.center.pop(i)
            self.center.pop(j - 1)
            self.center.append(center_new)
            self.nc -= 1
        self.start()

    def show(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        #设置标题  
        ax.set_title('start_%s' % self.current_i)
        
        c_l = ['b', 'g', 'c', 'm', 'y', 'k']
        #画散点图  
        ax.scatter(self.data[:,0], self.data[:,1], s = 1, c =  'r', marker='*')
        for i in range(len(self.center)):
            points = self.result[i]
            center = self.center[i]
            if len(points) > 5:
                # c_l = np.arctan2(center[1], center[0])
                ax.scatter(np.array([center[0]]), np.array([center[1]]), s = 50, c = np.array([c_l[i % 6]]))
                ax.annotate('%5f#%s'% (self.inner_mean_distance[i], len(self.result[i])), xy=(center[0], center[1]), xytext=(center[0], center[1]))
                ax.scatter(points[:,0], points[:,1], s = 1, c =  np.array([c_l[i % 6]] * len(points)))
        

        #设置X轴标签  
        plt.xlabel('lon')  
        #设置Y轴标签  
        plt.ylabel('lat')
        plt.show()

def get_lonlats(arr):
        lonlat = ''
        for i in range(len(arr)):
            lonlat = lonlat + str(arr[i][0]) + ',' + str(arr[i][1]) + ';'
        return lonlat

def show_all(matrix, isodata):
    matrix = np.array(matrix)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #设置标题  
    ax.set_title('start_last')
    
    c_l = ['b', 'g', 'c', 'm', 'y', 'k']
    #画散点图  
    ax.scatter(matrix[:,0], matrix[:,1], s = 1, c =  'r', marker='*')
    for i in range(len(isodata.center)):
        points = isodata.result[i]
        center = isodata.center[i]
        if len(points) > 5:
            # c_l = np.arctan2(center[1], center[0])
            ax.scatter(np.array([center[0]]), np.array([center[1]]), s = 50, c = np.array([c_l[i % 6]]))
            ax.annotate('%5f' % isodata.inner_mean_distance[i], xy=(center[0], center[1]), xytext=(center[0], center[1]))
            ax.scatter(points[:,0], points[:,1], s = 1, c =  np.array([c_l[i % 6]] * len(points)))
    #设置X轴标签  
    plt.xlabel('lon')  
    #设置Y轴标签  
    plt.ylabel('lat')
    plt.show()

def get_start_end(dict):
    dict_res = {}
    start_matrix, end_matrix  = [], []
    for value in dict.values():
        
        dict_res[value.id] = (value.start, value.end)

        lonlat = value.start.split(',')
        start_matrix.append([float(lonlat[0]), float(lonlat[1])])

        lonlat = value.end.split(',')
        end_matrix.append([float(lonlat[0]), float(lonlat[1])])
    return start_matrix, end_matrix, dict_res

def get_initial_set(matrix):
    initial_set = [10, 25, 5, 0.01, 0.01, 1, 10, 0.5]
    if len(matrix) == 0:
        return None
    elif len(matrix) == 1:
        initial_set[0] = 1
    elif initial_set[0] > len(matrix):
        initial_set[0] = len(matrix) // 2
    if len(matrix) < 50:
        initial_set[2] = 0
    return initial_set

if __name__ == "__main__":
    imei = '867012030284514'
    yixin = YixinTable()
    # yixin.load(r'jirm\experience-route\jirm.csv')
    start_matrix, end_matrix, dict = get_start_end(yixin.select(imei)) # 867012030302811  "867012030287491"

    # nc : 预选nc个聚类中心
    # K：希望的聚类中心个数
    # min_num：每个聚类中最少样本数
    # s：聚类域中样本的标准差阈值
    # c：两聚类中心之间的最短距离
    # L：在一次迭代中允许合并的聚类中心的最大对数
    # I：允许迭代的次数
    # k：分裂系数
    start_isodata = IsoData(get_initial_set(start_matrix), start_matrix)
    start_isodata.start()
    start_result = start_isodata.get_result()

    end_isodata = IsoData(get_initial_set(end_matrix), end_matrix)
    end_isodata.start()
    end_result = end_isodata.get_result()
    logging.debug('%s 起点聚合数：[%s], 终点聚合数：[%s].' % (imei, len(start_result), len(end_result)))
    # show_all(start_matrix, start_isodata)
    # show_all(end_matrix, end_isodata)
    for key, value in dict.items():
        start_mean = start_result[value[0]] if value[0] in start_result else ''
        end_mean = end_result[value[1]] if value[1] in end_result else ''
        # print(key, value[0], value[1], start_mean, end_mean, sep='-------')
        yixin.update(key, start_mean, end_mean)
    yixin.commit()