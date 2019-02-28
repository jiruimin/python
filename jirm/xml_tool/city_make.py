from urllib import request
import xml.etree.ElementTree as ET
import json

url = "http://w.mapbar.com/city/getCityDetail.json?city=%s"


def city_txt():
    citys = open('city.txt', 'r', encoding='utf-8')
    n_xml = ET.Element('citys')
    for line in citys:
        print(line)

        req = request.Request(url % (line))  # GET方法
        page = request.urlopen(req).read()   # 返回bytes类型
        page = page.decode('utf-8')          # bytes编码转string
        city_info = json.loads(page)['result']['city'][0]
        print('%s %s %s' %
              (line, city_info['cname'], city_info['ename']), end='\r\n')

        city = ET.SubElement(n_xml, 'city')
        adcode = ET.SubElement(city, 'adcode')
        name = ET.SubElement(city, 'name')
        py = ET.SubElement(city, 'py')
        adcode.text = line
        name.text = city_info['cname']
        py.text = city_info['ename']

    et = ET.ElementTree(n_xml)  # 生成文档对象
    et.write('te.xml', encoding='utf-8', xml_declaration=True)
    ET.dump(n_xml)

def city_list():
    with open('jirm/xml.tool/cityList.txt', 'r', encoding = 'utf-8') as city_file :
        city_xml = ET.Element('citys')
        for line in city_file:
            line = line.strip('\n')
            city = ET.SubElement(city_xml, 'city')
            adcode = ET.SubElement(city, 'adcode')
            name = ET.SubElement(city, 'name')
            py = ET.SubElement(city, 'py')
            name.text = line.split(',')[0]
            adcode.text = line.split(',')[1]
            py.text = line.split(',')[2]
        et = ET.ElementTree(city_xml)  # 生成文档对象
        et.write('jirm/xml.tool/te1.xml', encoding='utf-8', xml_declaration=True)
        ET.dump(city_xml)
city_list()