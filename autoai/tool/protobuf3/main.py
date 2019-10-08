from urllib import request
import OnlineRoutingService_V1_2_pb2
from google.protobuf import json_format

def get_request():
    req = request.Request("http://172.22.53.86:8079/v1/request")
    # req = request.Request("http://192.168.144.237:8090/v1/request")
    page = request.urlopen(req).read()
    with open("RouteRequestPb", 'wb') as ff :
        ff.write(page)
    routeRequest = OnlineRoutingService_V1_2_pb2.RouteRequest()
    routeRequest.ParseFromString(page)
    return routeRequest


if __name__ == "__main__":
    get_request()
    with open("RouteRequestPb", 'rb') as ff :
        b = ff.read()
    # req = request.Request("http://192.168.145.203:9097/v1/routing/initial", data=b, headers = {"Content-Type":"application/x-protobuf"})
    # req = request.Request("http://192.168.145.79:8097/v1/routing", data=b, headers = {"Content-Type":"application/x-protobuf"})
    req = request.Request("http://172.22.53.86:8079/v1/routing", data=b, headers = {"Content-Type":"application/x-protobuf"})
    # req = request.Request("http://192.168.144.237:8090/v1/routing", data=b, headers = {"Content-Type":"application/x-protobuf"})
    page = request.urlopen(req).read()   # 返回bytes类型
    routeResponse = OnlineRoutingService_V1_2_pb2.RouteResponse()
    routeResponse.ParseFromString(page)
    print(json_format.MessageToJson(routeResponse))