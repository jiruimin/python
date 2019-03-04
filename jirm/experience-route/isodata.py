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
from data_util import YixinTable 
import matplotlib.pyplot as plt




class IsoData(object):

    def __init__(self, initial_set, data):
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
        self.data = data  # 数据集

        self.center = []  # 聚类中心list
        self.result = []  # 聚类结果
        self.inner_mean_distance = []  # 类内平均距离

        self.all_mean_distance = 0  # 全部样本的总体平均距离
        # 预选nc个聚类中心
        for i in range(self.nc):
            d = self.data[int(self.data.shape[0] * i / self.nc),:]
            self.center.append(d)
        

    def start(self):
        if(self.current_i >= self.I):
            return self.center, self.result
        self.current_i += 1
        print('第[%s]轮循环......当前中心点：' % self.current_i, str(self.center), sep='')
        
        # 将全体样本分类
        self.result = self.center.copy()  # 聚类结果
        for i in range(self.data.shape[0]):
            point = self.data[i,:]
            # index = 0
            # dis = 99999
            # for j in range(len(self.cluster_center)):
            #     center = self.cluster_center[j]
            #     dis_1 = point * center.T
            #     if dis_1 < dis:
            #         index = j
            #         dis = dis_1
            index = 0
            dis_min = 9999
            for j in range(len(self.center)):
                dis_l = np.linalg.norm(self.center[j] - point)
                if dis_l < dis_min:
                    dis_min = dis_l
                    index = j
            self.result[index] = np.vstack((self.result[index], point))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        #设置标题  
        ax.set_title('start')
        
        c_l = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
        #画散点图  
        for i in range(len(self.center)):
            points = self.result[i]
            center = self.center[i]
            # c_l = np.arctan2(center[1], center[0])
            ax.scatter(np.array([center[0]]), np.array([center[1]]), s = 30, c = np.array([c_l[i % 8]]))
            ax.scatter(points[:,0], points[:,1], s = 10, c =  np.array([c_l[i % 8]] * len(points)))
        #设置X轴标签  
        plt.xlabel('lon')  
        #设置Y轴标签  
        plt.ylabel('lat')
        plt.show()
        ax.remove()
        # 删除第一个点，第一个点为类中心点，删除重复添加
        for i in range(len(self.result)):
            self.result[i] = np.delete(self.result[i], 0, axis = 0)

        # 删除样本条数小于min_num的分类
        for i in range(len(self.result) - 1, -1, -1):
            if len(self.result[i]) < self.min_num:
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
        # 迭代次数超过设置值 or 迭代次数是偶数次 or 分类数大于2K
        if self.current_i > self.I or self.current_i % 2 == 0 or self.nc >= 2 * self.K:
            # 合并
            self.step11()
        else:
            # 分裂
            self.step8_9_10()

    def step8_9_10(self):
        # 计算每类样本群的标准差向量
        print('第[%s]轮循环......分裂' % self.current_i)
        max_standard_index = []
        max_standard_dev = []
        for i in range(len(self.result)):
            std_vec = np.std(self.result[i], axis=0)
            index = np.argmax(std_vec)
            max_standard_index.append(index)
            max_standard_dev.append(std_vec[index])

        flag = False
        for i in range(len(max_standard_dev)):
            if max_standard_dev[i] > self.s and \
                    ((self.inner_mean_distance[i] > self.all_mean_distance and self.result[i].shape[0] > 2 * self.min_num) or self.nc < self.K / 2):
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
        print('第[%s]轮循环......合并' % self.current_i)
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

if __name__ == "__main__":
    yixin = YixinTable()
    # yixin.load(r'jirm\experience-route\jirm.csv')
    matrix = yixin.select('867012030288069') # 867012030288069/867012030289521

    # data = np.array([[0, 0], [1, 1], [2, 2], [4, 3], [5, 3], [4, 4], [5, 4], [6, 5]])


    # nc : 预选nc个聚类中心
    # K：希望的聚类中心个数
    # min_num：每个聚类中最少样本数
    # s：聚类域中样本的标准差阈值
    # c：两聚类中心之间的最短距离
    # L：在一次迭代中允许合并的聚类中心的最大对数
    # I：允许迭代的次数
    # k：分裂系数
    initial_set = [4, 20, 20, 0.001, 0.01, 1, 100, 0.5]
    isodata = IsoData(initial_set, matrix)
    isodata.start()
    center = np.array(isodata.center)

    # for i in range(len(result)):
    #     print('----------第' + str(i+1) + '个聚类----------')
    #     print(result[i])
    # initial_set = [2, 2, 1, 1, 4, 0, 4, 0.5]
    # isodata = IsoData(initial_set, data)
    # isodata.start()