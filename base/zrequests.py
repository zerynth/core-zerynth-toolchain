import requests
import datetime
import json
from .base import *
from .cfg import *
from .fs import *
from encodings import idna
import time

TimeoutException = requests.exceptions.Timeout
_ssl_verify = fs.path(fs.dirname(__file__),"certs.pem")
_default_timeout=5

################### json special type encoder
class ZjsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def zpost(url,data,headers={},auth=True,timeout=_default_timeout):
    hh = {"Content-Type": "application/json","User-agent":env.user_agent}
    if auth:
        token = get_token()
        hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.post(url=url, headers=hh, data=json.dumps(data, cls=ZjsonEncoder),timeout=timeout,verify=_ssl_verify)

def zget(url,headers={},params={},auth=True,token=None,stream=False):
    hh = {"Content-Type": "application/json","User-agent":env.user_agent}
    if auth:
        if auth=="conditional":
            token = get_token(True)
        else:
            if not token:
                token = get_token()
    if token: hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.get(url=url, headers=hh,timeout=_default_timeout,params=params,verify=_ssl_verify,stream=stream)

def zdelete(url,headers={},auth=True):
    hh = {"Content-Type": "application/json","User-agent":env.user_agent}
    if auth:
        token = get_token()
        hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.delete(url=url, headers=hh,timeout=_default_timeout,verify=_ssl_verify)

def zput(url, data,headers={},auth=True):
    hh = {"Content-Type": "application/json","User-agent":env.user_agent}
    if auth:
        token = get_token()
        hh.update({"Authorization": "Bearer "+token})
    hh.update(headers)
    return requests.put(url=url, headers=hh, data=json.dumps(data, cls=ZjsonEncoder),timeout=_default_timeout,verify=_ssl_verify)


def get_token(continue_if_none=False):
    tokdata = env.get_token()
    token = tokdata.token
    fn = warning if continue_if_none else critical
    if token:
        try:
            now = time.time()
            nowth = now-60*60*24*5 #5 days before expiration triggers renewal
            if tokdata.expires>nowth:
                return token
            elif tokdata.expires<nowth and tokdata.expires>now:
                #try to renew
                info("Token almost expired, trying to renew...")
                try:
                    res = zget(env.api.renew,token=token)
                    rj = res.json()
                    env.set_token(rj["token"])
                    return rj["token"]
                except Exception as e:
                    warning("Token renewal failed",exc=e)
            else:
                #force another login
                token = None
                fn("Token expired! Please run 'ztc login' to get a new one")
        except Exception as e:
            token=None
            fn("Critical error while retrieving authorization token:",exc=e)
    else:
        fn("No authorization token! Please run 'ztc login' to get one")
    return token
