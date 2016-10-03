import requests
import datetime
import json

hh = {"Content-Type": "application/json"}

################### json special type encoder
class ZjsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def zpost(url, headers, data):
    hh.update(headers)
    return requests.post(url=url, headers=hh, data=json.dumps(data, cls=ZjsonEncoder))

def zget(url, headers):
    hh.update(headers)
    return requests.get(url=url, headers=hh)

def zdelete(url, headers):
    hh.update(headers)
    return requests.delete(url=url, headers=hh)

def zput(url, headers, data):
    hh.update(headers)
    return requests.put(url=url, headers=hh, data=json.dumps(data, cls=ZjsonEncoder))

