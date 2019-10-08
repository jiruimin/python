from urllib import request
import xml.etree.ElementTree as ET
import json

url = "https://restapi.autoai.com/direction/v1/driving?ak=3py9yC7A197911n7n391fYoA59331Bq5&orig=%s&dest=%s&policy=0&num=1"

def ff(start, end):
    req = request.Request(url % (start, end))  # GET方法
    page = request.urlopen(req).read()   # 返回bytes类型
    page = page.decode('utf-8')          # bytes编码转string
    root = json.loads(page)
    if root['status'] != 200:
        return
    steps = json.loads(page)['data']['routes'][0]['steps']
    route_length = 0
    route = ''
    for step in steps:
        route += step['lonlats']
        route_length += step['dis']
    route = route.replace(";", "|")
    fw = open("E:/res2.txt",'a')
    fw.write('route_length=%s&route=%s\r\n' % (route_length, route))


if __name__ == "__main__":
    with open('F:/rtic.txt', 'r', encoding='utf-8') as f:
        for line in f.read().splitlines():
            sta = line.split(",")[2]
            if sta == "4":
                print(line)
        
        
    


