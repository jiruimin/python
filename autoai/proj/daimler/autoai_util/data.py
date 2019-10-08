import json
import pymongo as pm
import logging

__mongo_host__ = '192.168.145.79'
__mongo_port__ = 27017

def lonlat():
    file = open('test_data_v2.json','r')
    routes = json.load(file)['routes']
    for route in routes:
        commute_route_id = route['commute_route_id']
        start = ''
        end = ''
        for track in route['tracks']:
            session_id = track['session_id']
            start = start + '%s,%s;' % (track['points'][0]['long'], track['points'][0]['lat'])
            end = end + '%s,%s;' % (track['points'][len(track['points']) - 1]['long'], track['points'][len(track['points']) - 1]['lat'])
            lonlat = ''
            for en in track['points']:
                lonlat = lonlat + '%s,%s;' % (en['long'], en['lat'])
            print('%s %s %s' % (commute_route_id, session_id, lonlat))
        print('start %s' % start)
        print('end %s' % end)


def up_mongo():
        client = pm.MongoClient(__mongo_host__, __mongo_port__)  # 端口号是数值型
        db = client['location-platform']
        stb = db['PartSplit']
        stb_copy = db['PartSplit_copy']
        stb_org = db['t_yixin_org_data']
        datas = stb.find({},{"extend":0,"parts":0,"points":0,"_class":0})
        # res = self._cursor.fetchall()
        k = 0
        for en in datas:
            org = stb_org.find_one({'_id':'%s#%s' % (en['_id'], en['imei'])})
            if org is not None:   
                dict = {}
                dict['imei'] = en['imei']
                dict['vin'] = en['vin']
                dict['startTime'] = en['startTime']
                dict['endTime'] = en['endTime']
                dict['runTime'] = en['runTime']
                dict['interval'] = en['interval']
                dict['speed'] = en['speed']
                dict['startLat'] = en['startLat']
                dict['startLon'] = en['startLon']
                dict['endLat'] = en['endLat']
                dict['endLon'] = en['endLon']
                dict['org'] = org['orgLonlats']
                stb_copy.insert_one(dict)
            k += 1
            print(k)

if __name__ == "__main__":
    up_mongo()