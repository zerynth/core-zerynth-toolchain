import requests
import datetime
import json
from .base import *
from .cfg import *
import base64
import time


################### json special type encoder
class ZjsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def zpost(url,data,headers={},auth=True):
    hh = {"Content-Type": "application/json"}
    if auth:
        token = get_token()
        hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.post(url=url, headers=hh, data=json.dumps(data, cls=ZjsonEncoder),timeout=5)

def zget(url,headers={},auth=True,token=None):
    hh = {"Content-Type": "application/json"}
    if auth:
        if not token:
            token = get_token()
        hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.get(url=url, headers=hh,timeout=5)

def zdelete(url,headers={},auth=True):
    hh = {"Content-Type": "application/json"}
    if auth:
        token = get_token()
        hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.delete(url=url, headers=hh,timeout=5)

def zput(url, data,headers={},auth=True):
    hh = {"Content-Type": "application/json"}
    if auth:
        token = get_token()
        hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.put(url=url, headers=hh, data=json.dumps(data, cls=ZjsonEncoder),timeout=5)


def decode_base64(data):
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += '='* (4 - missing_padding)
    return base64.standard_b64decode(data)

def get_token():
    token = env.var.get("token")
    if token:
        try:
            pl = token.split(".")[1]
            js = json.loads(decode_base64(pl).decode("utf-8"))
            now = time.time()
            nowth = now-60*60*24*5 #5 days before expiration triggers renewal
            if js["exp"]>nowth:
                return token
            elif js["exp"]<nowth and js["exp"]>now:
                #try to renew
                info("Token almost expired, trying to renew...")
                try:
                    res = zget(env.api.renew,token=token)
                    rj = res.json()
                    env.var.set("token",rj["token"])
                    env.save()
                    return rj["token"]
                except Exception as e:
                    warning("Token renewal failed",exc=e)
            else:
                #force another login
                critical("Token expired! Please run 'ztc login' to get a new one")
        except Exception as e:
            critical("Critical error while retrieving autorization token:",exc=e)
    else:
        critical("No authorization token! Please run 'ztc login' to get one")
    return token
