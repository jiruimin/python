#!/usr/bin/python3

'''斗鱼客户端主程序，封装一些接本的操作'''

import json

import select
import socket
import sqlite3
import threading
import time
from urllib import request

__table_name__ = 'danmu'
__roomid = '276200'


class _socket(socket.socket):
    """docstring for socket"""

    def push(self, data_dict):
        '''将入参dict拼接成字节流,并传到socket中'''
        data = ''
        for k, v in data_dict.items():
            data += ('%s@=%s/' % (k, v))
            
        data = data[0:-1]
        s = (len(data) + 9).to_bytes(4, byteorder='little') * 2 
        s += (689).to_bytes(2, byteorder='little')
        s += b'\x00\x00'
        s += data.encode('utf-8') + b'\x00'
        self.sendall(s)

    def pull(self):
        '''获取并解析socket接收到的字节流，返回解析后的dict内容'''
        res = {}
        data = self.recv(10240)
        length = int.from_bytes(data[0:4], byteorder='little')
        msg_type = int.from_bytes(data[8:10], byteorder='little')
        if msg_type == 690:
            content = data[12:12 + length - 9].decode('utf-8', 'ignore')
            for en in filter(lambda x: x != '', content.split('/')):
                res[en.split('@=', 2)[0]] = en.split('@=', 2)[1]
        return res


class _DouyuClient(object):
    """docstring for DouyuClient"""

    def __init__(self, roomid):
        self.__roomid = roomid
        self._owner = ''
        self._msg_pipe = []
        self._gift_dict = {}
        self.danmuThread, self.heartThread = None, None
        self.danmu_socket = _socket()
        self.danmu_socket.connect(('openbarrage.douyutv.com', 8601))
        self.danmu_socket.settimeout(3)

    def _start(self):
        if self._is_online():
            self._joing_room_group()
            self._wrap_thread()

    def _joing_room_group(self):
        self.danmu_socket.push({'type': 'loginreq', 'roomid': self.__roomid})
        self.danmu_socket.push(
            {'type': 'joingroup', 'rid': self.__roomid, 'gid': '-9999'})

    def _socket_timeout(self, fn):
        def __socket_timeout(*args, **kwargs):
            try:
                fn(*args, **kwargs)
            except Exception as e:
                raise e
        return __socket_timeout

    def _create_thread_fn(self):
        @self._socket_timeout
        def _keep_alive(self):
            while True:
                self.danmu_socket.push(
                    {'type': 'keeplive', 'tick': int(time.time())})
                time.sleep(30)

        @self._socket_timeout
        def _get_danmu(self):
            while True:
                if not select.select([self.danmu_socket], [], [], 1)[0]:
                    continue
                danmu = self.danmu_socket.pull()
                self._msg_pipe.append(danmu)
        return _keep_alive, _get_danmu

    def _wrap_thread(self):
        heart_beat, get_danmu = self._create_thread_fn()
        self.heartThread = threading.Thread(target=heart_beat, args=(self,))
        self.heartThread.setDaemon(True)
        self.heartThread.start()
        self.danmuThread = threading.Thread(target=get_danmu, args=(self,))
        self.danmuThread.setDaemon(True)
        self.danmuThread.start()

    def _is_online(self):
        url = 'http://open.douyucdn.cn/api/RoomApi/room/%s' % self.__roomid
        headers = {'Accept': r'application/json,*/*;q=0.',
                   'User-Agent': r'Mozilla/5.0 Chrome/68.0.3440.106'}
        req = request.Request(url, headers=headers)
        response = request.urlopen(req, timeout=3)
        resp = json.loads(response.read().decode('utf-8'))
        if resp['error'] == 0 and resp['data']['room_status'] == '1':
            print(resp['data']['room_id'], '主播直播中......')
            self._owner = resp['data']['owner_name']
            for dgb in resp['data']['gift']:
                self._gift_dict[dgb['id']] = {'name': dgb['name'],
                                              'type': dgb['type'],
                                              'pc': dgb['pc']}
            return True
        else:
            print(resp['data']['room_id'], '主播未开播......')
            return False


class DouyuClient(_DouyuClient):
    """docstring for """

    def __init__(self, roomid):
        # global __table_name
        super(DouyuClient, self).__init__(roomid)
        self.__functionDict = {'default': lambda x: 0}
        self._conn = sqlite3.connect('database')
        self._cursor = self._conn.cursor()
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + __table_name__ +
                             " ('uid' TEXT NOT NULL,'nn' TEXT NOT NULL, \
                              'type' TEXT NOT NULL, 'txt' TEXT, 'gfid' TEXT,\
                              'gfcnt' TEXT, 'hits' TEXT,  'roomid' TEXT,\
                              'owner' TEXT, 'createtime' TEXT NOT NULL)",)

    def start(self):
        self._start()
        while True:
            if self._msg_pipe:
                msg = self._msg_pipe.pop()
                fn = self.__functionDict.get(msg.get('type', 'default'),
                                             lambda x: 0)
                fn(msg)
            else:
                time.sleep(1)

    def danmu(self, fn):
        self.__functionDict['chatmsg'] = fn

    def gift(self, fn):
        self.__functionDict['dgb'] = fn


if __name__ == '__main__':
    client = DouyuClient(__roomid)

    def gift_info(gfid):
        if gfid == '824':
            return '粉丝荧光棒'
        g_dict = client._gift_dict.get(gfid, None)
        if not g_dict:
            return gfid
        else:
            return '价值%s%s的%s' % (g_dict['pc'],
                                  '元' if (g_dict['type'] == '2') else '鱼丸',
                                  g_dict['name'])

    @client.danmu
    def danmu(msg):
        print('%s %s(%s): %s' %
              (time.strftime('%H:%M:%S', time.localtime()),
               msg['nn'], msg['uid'], msg['txt']))
        client._cursor.execute("INSERT INTO " + __table_name__ +
                               "('uid', 'nn', 'type', 'txt', 'roomid',\
                                'owner', 'createtime')\
                                VALUES(?, ?, ?, ?, ?, ?, ?)",
                               (msg['uid'], msg['nn'], msg['type'], msg['txt'],
                                __roomid, client._owner,
                                time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime())))
        client._conn.commit()

    @client.gift
    def gift(msg):
        print('%s %s(%s): 送出礼物[%s]' %
              (time.strftime('%H:%M:%S', time.localtime()),
               msg['nn'], msg['uid'], gift_info(msg['gfid'])))
        if msg['gfid'] == '824':
            return
        client._cursor.execute("INSERT INTO " + __table_name__ +
                               "('uid', 'nn', 'type', \
                                'txt', 'gfid', 'gfcnt', 'hits', \
                                'roomid', 'owner', 'createtime')\
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (msg['uid'], msg['nn'], msg['type'],
                                gift_info(msg['gfid']), msg['gfid'],
                                msg['gfcnt'], msg['hits'],
                                __roomid, client._owner,
                                time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime())))
        client._conn.commit()
    client.start()
