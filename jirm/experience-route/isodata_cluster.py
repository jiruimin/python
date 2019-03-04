# coding=utf8

# initial_set为初始设置，依次代表如下：
# nc : 预选nc个聚类中心
# K：希望的聚类中心个数
# min_num：每个聚类中最少样本数
# s：聚类域中样本的标准差阈值
# c：两聚类中心之间的最短距离
# L：在一次迭代中允许合并的聚类中心的最大对数
# I：允许迭代的次数
# k：分裂系数

import math

from k_means_cluster import classify, get_newcluster  
from max_min_cluster import get_distance


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

        self.step1()

    def step1(self):

        # 预选nc个聚类中心

        for i in range(self.nc):
            self.cluster_center.append(self.data[i])
            self.result.append([self.data[i]])
        self.step2()

    def step2(self):

        # 最近邻规则分类

        # self.result = []
        self.result = classify(self.data, self.cluster_center)
        self.step3()

    def step3(self):

        # 判断Sj中样本数Nj是否小于min_num

        for i in range(len(self.result)):
            if len(self.result[i]) < self.min_num:
                self.result.pop(i)
                self.cluster_center.pop(i)
                self.nc -= 1
        self.step4()

    def step4(self):

        # 修正各聚类中心值

        self.cluster_center = get_newcluster(self.result)
        self.step5_6()

    def step5_6(self):

        # 计算类内平均距离以及全部样本的总体平均距离

        for i in range(len(self.result)):
            inner_dis = 0
            for j in range(len(self.result[i])):
                inner_dis += get_distance(self.result[i][j], self.cluster_center[i])
            self.all_mean_distance += inner_dis
            inner_dis = inner_dis / len(self.result[i])
            self.inner_mean_distance.append(inner_dis)
        self.all_mean_distance = self.all_mean_distance / len(self.data)
        self.step7()

    def step7(self):

        # 判断是进行分裂还是合并

        if self.current_i is self.I:
            self.c = 0
            self.step11_12_13_14()
        elif self.nc <= self.K / 2:
            self.step8_9_10()
        elif (self.current_i % 2 is 0) or self.nc >= 2 * self.K:
            self.step11_12_13_14()
        else: 
            self.step8_9_10()

    def step8_9_10(self):

        # 第八、九、十步：计算每个聚类中样本的标准差向量；求每个标准差向量的最大分量；
        # 在最大分量集中，根据条件判断下一步

        index_list = [0 for i in range(len(self.result))]  # 对应最大分量的分量序号
        max_standard_dev = [0 for i in range(len(self.result))]  # 最大分量集

        for i in range(len(self.result)):
            temp = 0
            # 记录标准差向量的最大分量及对应分量序号
            max_index = 0
            index = 0

            for j in range(len(self.data[0])):
                for k in range(len(self.result[i])):
                    temp += math.pow(self.result[i][k][j]- self.cluster_center[i][j], 2)
                temp = math.sqrt(temp / len(self.result[i]))
                if temp > max_index:
                    max_index = temp
                    index = j
                index_list[i] = index
                max_standard_dev[i] = max_index

        # 第十步：判断
        for i in range(len(max_standard_dev)):
            new_cluster1 = [0 for m in range(len(self.data[0]))]
            new_cluster2 = [0 for m in range(len(self.data[0]))]
            if max_standard_dev[i] > self.s and \
                    ((self.inner_mean_distance[i] > self.all_mean_distance and len(self.result[i]) > 2 * (self.min_num + 1)) or self.nc <= self.K / 2):
                for j in range(len(self.cluster_center[i])):
                    if j is not index_list[i]:
                        new_cluster1[j] = self.cluster_center[i][j]
                        new_cluster2[j] = self.cluster_center[i][j]
                    else:
                        new_cluster1[j] = self.cluster_center[i][index_list[i]] + self.k * max_standard_dev[i]
                        new_cluster2[j] = self.cluster_center[i][index_list[i]] - self.k * max_standard_dev[i]
                self.cluster_center.append(new_cluster1)
                self.cluster_center.append(new_cluster2)
                self.cluster_center.pop(i)
                self.current_i += 1
                self.nc += 1
                print('分裂')
                self.step2()
            else:
                self.step11_12_13_14()

    def step11_12_13_14(self):
        print('合并')
        # 第十一、十二步：计算所有聚类中心之间的距离，并将小于c的值存入list按升序排列
        # 储存小于c的距离以及对应聚类中心下标的map

        dis_index = {}
        for i in range(1, self.nc -1):
            for j in range(i+1, self.nc):
                indexes = [0, 0]  # 下标数组
                dis_temp = get_distance(self.cluster_center[i], self.cluster_center[j])
                if dis_temp < self.c:
                    indexes[0] = i
                    indexes[1] = j
                    dis_index[dis_temp] = indexes

        # 距离按升序排列后的list
        dis_list = list(dis_index.keys())
        # 第十三步：合并
        if(len(dis_list) > 0):
            for i in range(self.L):
                # 即将合并的聚类的标号
                index = dis_index.get(dis_list[i])
                # 已经合并过的聚类的标号
                already_index = []
                # 判断是否合并过
                if not (index[0] in already_index  or index[1] in already_index):
                    # 新聚类中心
                    new_cluster = [0 for i in range(len(self.data[0]))]
                    for j in range(len(new_cluster)):
                        new_cluster[j] = (len(self.result[index[0]]) * self.cluster_center[index[0]][j]
                                        + len(self.result[index[1]]) * self.cluster_center[index[1]][j]) \
                                        / (len(self.result[index[0]]) + len(self.result[index[j]]))
                    self.cluster_center.append(new_cluster)
                    self.cluster_center.pop(index[0])
                    self.cluster_center.pop(index[1])
                    already_index.append(index[0])
                    already_index.append(index[1])
                    self.nc -= 1

        # 第十四步：判断
        if self.current_i is not self.I:
            # flag = input("是否需要修改参数,输入“y”确认修改，“n”取消\n")
            print(self.current_i)
            flag = 'n'
            if flag == "y":
                self.nc = int(input("nc:"))
                self.K = int(input("K:"))
                self.min_num = int(input("min_num:"))
                self.s = float(input("s:"))
                self.c = float(input("c:"))
                self.L = int(input("L:"))
                self.I = int(input("I:"))
                self.k = float(input("k:"))
                self.current_i += 1
                self.step1()
            else:
                self.current_i += 1
                self.step2()
# 测试ISODATA
# data = [[0, 0], [1, 1], [2, 2], [4, 3], [5, 3], [4, 4], [5, 4], [6, 5]]
# initial_set = [1, 2, 1, 1, 4, 0, 4, 0.5]
# 
# isodata = IsoData(initial_set, data)
# result = isodata.result
# 
# for i in range(len(result)):
#     print "----------第" + str(i+1) + "个聚类----------"
#     print result[i]

# 结果：
# C:\Python27\python.exe C:/Users/14344/Cluster_Algorithm/test.py
# 是否需要修改参数,输入“y”确认修改，“n”取消
# n
# ----------第1个聚类----------
# [[4, 3], [5, 3], [4, 4], [5, 4], [6, 5]]
# ----------第2个聚类----------
# [[0, 0], [1, 1], [2, 2]]
# 