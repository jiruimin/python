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

        self.current_i = 1  # 目前迭代的次数
        self.data = data  # 数据集

        self.cluster_center = []  # 聚类中心list
        self.result = []  # 聚类结果
        self.inner_mean_distance = []  # 类内平均距离

        self.all_mean_distance = 0  # 全部样本的总体平均距离

        

    def start(self):
        self.cluster_center = []  # 聚类中心list
        self.result = []  # 聚类结果
        
        # 预选nc个聚类中心
        for i in range(self.nc):
            d = self.data[int(self.data.shape[0] * i / self.nc),:]
            self.cluster_center.append(d)
            self.result.append(d)
        
        # 将全体样本分类
        for i in range(self.data.shape[0]):
            point = self.data[i]
            index = 0
            dis = 0
            for j in range(len(cluster_center)):
                
