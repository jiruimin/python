from yixin_data import YixinTable
import pymongo as pm
import isodata
import logging
import track_classify

__mongo_host__ = '192.168.145.79'
__mongo_port__ = 27017

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
    # 获取连接
    client = pm.MongoClient(__mongo_host__, __mongo_port__)  # 端口号是数值型
    # 连接数据库location-platform
    db = client['location-platform']
    # 获取集合
    stb1 = db.PartSplit
    stb2 = db.t_yixin_org_data

    datas = stb1.distinct('imei')

    k, l = 0, len(datas)
    for imei in datas:
        k += 1
        logging.info('[%s/%s][%s] start...' % (k, l, imei))
        print('[%s/%s][%s] start...' % (k, l, imei))
        yixin = YixinTable()
        yixin.load(imei)   # 867012030302811  "867012030287491"


        start_matrix, end_matrix, dict = isodata.get_start_end(yixin.select(imei))  # 867012030302811  "867012030287491"

        if(len(start_matrix) == 0 or len(end_matrix) == 0 or len(dict) == 0):
            logging.info('%s data error...' % imei)
            print('%s data error...' % imei)
            continue
        # nc : 预选nc个聚类中心
        # K：希望的聚类中心个数
        # min_num：每个聚类中最少样本数
        # s：聚类域中样本的标准差阈值
        # c：两聚类中心之间的最短距离
        # L：在一次迭代中允许合并的聚类中心的最大对数
        # I：允许迭代的次数
        # k：分裂系数
        start_isodata = isodata.IsoData(get_initial_set(start_matrix), start_matrix)
        start_isodata.start()
        if not start_isodata.flag:
            continue
        
        end_isodata = isodata.IsoData(get_initial_set(end_matrix), end_matrix)
        end_isodata.start()
        if not end_isodata.flag:
            continue
        start_result = start_isodata.get_result()
        end_result = end_isodata.get_result()
        logging.info('%s start classify ：[%s], end classify：[%s].' % (imei, len(start_result), len(end_result)))
        print('%s start classify ：[%s], end classify：[%s].' % (imei, len(start_result), len(end_result)))

        for key, value in dict.items():
            start_mean = start_result[value[0]] if value[0] in start_result else ''
            end_mean = end_result[value[1]] if value[1] in end_result else ''
            yixin.update(key, start_mean, end_mean)
        yixin.commit()

        yixin_dict = yixin.select(imei)
        yixin_dict = track_classify.classify(yixin_dict)
        for key,value in yixin_dict.items():
            lonlats_list = []
            yixin_ids = []
            for data in value:
                lonlats_list.append(data.org)
                yixin_ids.append(data.id)
            index = track_classify.get_experience_lonlat(lonlats_list)
            yixin.insert_experience_org(value[0].imei, value[0].vin,  value[0].startMean,  value[0].endMean,
                    value[0].startTime, str(yixin_ids), yixin_ids[index], lonlats_list[index])
        yixin.commit()