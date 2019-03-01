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
        self.result = self.center.copy()  # 聚类结果
        
        # 将全体样本分类
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
            dis_l = np.linalg.norm(self.center - np.array([point for i in range(len(self.center))]))
            index = np.argmin(dis_l[:,0])
            self.result[index] = np.vstack((self.result[index], point))

        # 删除第一个点，第一个点为类中心点，删除重复添加
        for i in range(len(self.result)):
            self.result[i] = np.delete(self.result[i], 0, axis = 0)

        # 删除样本条数小于min_num的分类
        for i in range(len(self.result)):
            if len(self.result[i]) < self.min_num:
                self.result.pop(i)
                self.center.pop(i)
                self.nc -= 1
                # 重新分类
                self.start()
    
    # 调整各类型中心点 + 计算类内平均距离 + 计算总体平均距离
    def step4_5_6(self):
        # 调整各类型中心点 + 计算类内平均距离
        self.inner_mean_distance = []
        self.center = []  # 聚类中心list
        for i in range(len(self.result)):
            sum_1 = np.mean(self.result[i], axis=0)
            dis_l = np.linalg.norm(self.result[i] - np.array([sum_1 for i in range(self.result[i].shape[0])]))
            self.inner_mean_distance.append(np.mean(dis_l, axis = 0)[0])
            self.center.append(sum_1)

        # 计算总体平均距离
        all_mean_distance = 0
        all_mean_distance_num = 0
        for i in range(len(self.inner_mean_distance)):
            all_mean_distance += (self.inner_mean_distance[i] * self.result[i].shape[0])
            all_mean_distance_num += self.result[i].shape[0]
        self.all_mean_distance = all_mean_distance / all_mean_distance_num
        

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
        max_standard_index = []
        max_standard_dev = []
        for i in range(len(self.result)):
            std_vec = np.std(self.result[i], axis=0)
            index = np.argmax(std_vec, axis=1)
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
                self.center.append(center[max_standard_index[i]] - self.k * max_standard_dev[i])
                self.center.append(center[max_standard_index[i]] + self.k * max_standard_dev[i])
                flag = True
        if(flag):
            self.start()
        else:
            self.step11()

    # 合并操作
    def step11(self):
        dis_center = 999
        for i in range(len(self.center)):
            for j in range(i + 1, len(self.center)):
                dis_l = np.linalg.norm(self.center[i] - self.center[j])
                if dis_l < dis_center:
                    min_center = (i, j)
        
        if min_center < self.c:
            center_new = (self.center[i] * self.result[i].shape[0] + self.center[j] * self.result[j].shape[0]) / (self.result[i].shape[0] + self.result[j].shape[0])
            self.center.pop(i)
            self.center.pop(j - 1)
            self.center.append(center_new)
            self.nc -= 1
        self.start()