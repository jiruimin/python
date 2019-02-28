#!/usr/bin/python3

'''计算一定时间段内路况的平均值，用于计算早晚高峰期，平时的路况平均路况'''


class LinkTmc(object):  
    """docstring for LinkTmc"""
    def __init__(self, link, up_status, up_speed, down_status, down_speed):
        super(LinkTmc, self).__init__()
        self.link = link
        self.up_status = up_status
        self.up_speed = up_speed
        self.down_status = down_status
        self.down_speed = down_speed


def read_tmc(fileName):
    tmc = {}

    tmc_data = open(fileName, 'rb').read()
    updatetime = int.from_bytes(tmc_data[0:8], byteorder='big')
    tmc_num = int.from_bytes(tmc_data[8:12], byteorder='big')
    index = 16
    print(len(tmc_data), tmc_num, sep=',')
    i = 0
    for i in range(tmc_num):
        link = int.from_bytes(tmc_data[index:index + 4], byteorder='big')
        index += 4

        up_status = tmc_data[index] >> 4 & 0x0f
        up_speed = tmc_data[index] & 0xf0 << 8 | tmc_data[index + 1] & 0xff
        index = index + 2

        down_status = tmc_data[index] >> 4 & 0x0f
        down_speed = tmc_data[index] & 0xf0 << 8 | tmc_data[index + 1] & 0xff
        index = index + 2
        tmc[link] = LinkTmc(link, up_status, up_speed, down_status, down_speed)
        # print(i, link, up_status, up_speed, down_status, down_speed, sep=',')
    print(updatetime)


read_tmc('201810211334')
