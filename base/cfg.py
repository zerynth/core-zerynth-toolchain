import sys
import sqlite3
from .base import *
from .fs import *
import json
import base64
import os

__all__=['env','Var']

class Var():
    def __init__(self, _dict={},recursive=True):
        self._v=dict(_dict)
        for k,v in _dict.items():
            if isinstance(v,dict) and recursive:
                self._v[k] = Var(v)
            else:
                self._v[k] = v

    def __getattr__(self,attr):
        return self._v[attr]

    def to_dict(self):
        d = {}
        for k,v in self._v.items():
            if isinstance(v,Var):
                d[k]=v.to_dict()
            else:
                d[k]=v
        return d

    def set(self,key,value):
        self._v[key] = Var(value) if isinstance(value,dict) else value

    def get(self,key,default=None):
        return self._v.get(key,default)

    def __str__(self):
        return str(self._v)


class Environment():
    
    def __init__(self):
        pass

    def dirs(self):
        prefix = fs.homedir()
        for x in self.__dict__:
            if isinstance(self[x],str) and self[x].startswith(prefix):
                yield self[x]


    def __getitem__(self,key):
        return getattr(self,key)
    

    def load(self,cfgdir):
        try:
            js = fs.get_json(fs.path(cfgdir,"config.json"))
            self.var = Var(js)
            self._var = js
        except Exception as e:
            critical("can't load configuration",exc=e)

    def save(self,cfgdir=None):
        try:
            if not cfgdir:
                cfgdir=self.cfg
            js = fs.set_json(self.var.to_dict(),fs.path(cfgdir,"config.json"))
        except Exception as e:
            critical("can't save configuration",exc=e)


    def load_dbs(self,cfgdir,dbname):
        try:
            #js = fs.get_json(fs.path(cfgdir,dbname))
            self._dbs_cfgdir=cfgdir
            self._dbs_dbname=dbname
            self._dbs = sqlite3.connect(fs.path(cfgdir,dbname),check_same_thread=False)
            self._dbs.execute("CREATE TABLE IF NOT EXISTS aliases (alias TEXT PRIMARY KEY, uid TEXT, target TEXT, name TEXT, chipid TEXT, remote_id TEXT, classname TEXT)")
            self._dbs.execute("CREATE UNIQUE INDEX IF NOT EXISTS aliases_idx ON aliases(alias)")
            self._dbs.execute("CREATE UNIQUE INDEX IF NOT EXISTS uid_idx ON aliases(uid)")
            self._dbs.execute("CREATE INDEX IF NOT EXISTS chip_idx ON aliases(chipid)")
        except Exception as e:
            self._dbs = None

    def save_dbs(self):
        try:
            self._dbs.commit()
        except Exception as e:
            critical("can't save configuration",exc=e)

    def load_repo_list(self):
        try:
            fs.get_json(fs.path(env.cfg,"repos.cfg"))
        except:
            pass
        return []

    def get_dev(self,key):
        res = {}
        for row in self._dbs.execute("select * from aliases where alias=? or uid=?",(key,key)):
            res[row[0]]=Var({"alias":row[0],"uid":row[1],"target":row[2],"name":row[3],"chipid":row[4],"remote_id":row[5],"classname":row[6]})
        return res

    def get_dev_by_alias(self,alias):
        res = []
        for row in self._dbs.execute("select * from aliases where alias like '"+alias+"%'"):
            res.append(Var({"alias":row[0],"uid":row[1],"target":row[2],"name":row[3],"chipid":row[4],"remote_id":row[5],"classname":row[6]}))
        return res

    def put_dev(self,dev):
        if not isinstance(dev,Var):
            dev = Var(dev)
        self._dbs.execute("insert or replace into aliases values(?,?,?,?,?,?,?)",(dev.alias,dev.uid,dev.target,dev.name,dev.chipid,dev.remote_id,dev.classname))
        self._dbs.commit()

    def del_dev(self,dev):
        self._dbs.execute("delete from aliases where alias=?",(dev.alias,))
        self._dbs.commit()

    def get_all_dev(self):
        for row in self._dbs.execute("select * from aliases"):
            yield Var({"alias":row[0],"uid":row[1],"target":row[2],"name":row[3],"chipid":row[4],"remote_id":row[5],"classname":row[6]})

    def make_dist_dirs(self,distpath):
        fs.makedirs(self.ztc_dir(distpath))
        fs.makedirs(self.lib_dir(distpath))
        fs.makedirs(self.stdlib_dir(distpath))
        fs.makedirs(self.studio_dir(distpath))
        fs.makedirs(self.docs_dir(distpath))
        fs.makedirs(self.examples_dir(distpath))


    def get_token(self):
        # get token
        try:
            token = Var(fs.get_json(fs.path(env.cfg,"token.json")))
        except:
            token = Var({
                "token": None,
                "expires":0,
                "type": None
            })
        return token

    def set_token(self,rawtoken):
        pl = rawtoken.split(".")[1]
        js = json.loads(decode_base64(pl).decode("utf-8"))
        token = {
            "token":rawtoken,
            "expires":js["exp"],
            "type": None
        }
        fs.set_json(token,fs.path(env.cfg,"token.json"))


def decode_base64(data):
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += '='* (4 - missing_padding)
    return base64.standard_b64decode(data)



env=Environment()


# ####
#     .Zerynth/
#         cfg/
#             devdb/
#         workspace/
#         sys/
#         tmp/
#         nest/
#         dist/
#             version/
#                 ztc/
#                 libs/
#                 nest/
#                 stdlib/
#                 vhal/
#                 studio/
#                 docs/
#                 devices/
#                 examples/
                


def init_cfg():
    # platform
    env.nbits = "64" if sys.maxsize > 2**32 else "32"
    if sys.platform.startswith("win"):
        env.platform="windows"+env.nbits
    elif sys.platform.startswith("linux"):
        env.platform="linux"+env.nbits
    elif sys.platform.startswith("darwin"):
        env.platform="mac"

    env.is_windows = lambda : env.platform.startswith("win")
    env.is_unix = lambda : not env.platform.startswith("win")
    env.is_mac = lambda : env.platform.startswith("mac")
    env.is_linux = lambda : env.is_unix() and not env.is_mac()

    # main directories TODO: change zdir to official zdir
    zdir = "zerynth2" if env.is_windows() else ".zerynth2"
    env.home      = fs.path(fs.homedir(),zdir)
    env.cfg       = fs.path(env.home,"cfg")
    env.env       = fs.path(env.home,"env")
    env.devdb     = fs.path(env.home,"cfg","devdb")
    env.tmp       = fs.path(env.home,"tmp")
    env.sys       = fs.path(env.home,"sys")
    env.workspace = fs.path(env.home,"workspace")
    env.vms       = fs.path(env.home,"vms")
    env.edb       = fs.path(env.home,"cfg","edb")
    env.zdb       = fs.path(env.home,"cfg","zdb")
    env.idb       = fs.path(env.home,"cfg","idb")


    # load configuration
    env.load(env.cfg)
    env.load_dbs(env.cfg,"devices.db")
    #env.load_zpack_db(env.zdb,"packages.db")
    #env.load_ipack_db(env.idb,"packages.db")
    version = env.var.version
    if os.environ.get("ZERYNTH_TEST",0)==1:
        env.git_url = "http://localhost/git"
        env.backend="http://localhost/v1"
    else:
        env.git_url ="https://backend.zerynth.com/git"
        env.backend="https://backend.zerynth.com/v1"

    # dist directories
    env.dist      = fs.path(env.home,"dist",version)
    env.ztc       = fs.path(env.home,"dist",version,"ztc")
    env.libs      = fs.path(env.home,"dist",version,"libs")
    env.nest      = fs.path(env.home,"dist",version,"nest")
    env.stdlib    = fs.path(env.home,"dist",version,"stdlib")
    env.vhal      = fs.path(env.home,"dist",version,"vhal") 
    #env.vhal      = fs.path(fs.homedir(),".zerynth","env","core","official","vhal") #TODO: remove
    env.studio    = fs.path(env.home,"dist",version,"studio")
    env.docs      = fs.path(env.home,"dist",version,"docs")
    env.examples  = fs.path(env.home,"dist",version,"examples")
    env.devices    = fs.path(env.home,"dist",version,"devices")
    #env.devices    = fs.path(fs.homedir(),"git","ZerynthBoards") #TODO: remove

    env.dist_dir = lambda x: fs.path(env.home,"dist",x)
    env.ztc_dir = lambda x: fs.path(x,"ztc")
    env.lib_dir = lambda x: fs.path(x,"libs")
    env.stdlib_dir = lambda x: fs.path(x,"stdlib")
    env.studio_dir = lambda x: fs.path(x,"studio")
    env.vhal_dir = lambda x: fs.path(x,"vhal")
    env.devices_dir = lambda x: fs.path(x,"devices")
    env.docs_dir = lambda x: fs.path(x,"docs")
    env.examples_dir = lambda x: fs.path(x,"examples")


    # set global temp dir
    fs.set_temp(env.tmp)

    # create dirs
    fs.makedirs(env.dirs())

    # backend & api
    #env.backend="https://backend.zerynth.com/v1"
    env.api = Var({
        "project":env.backend+"/projects",
        "renew":env.backend+"/user/renew",
        "sso":env.backend+"/sso",
        "pwd_reset":env.backend+"/user/reset",
        "devices":env.backend+"/devices",
        "vm":env.backend+"/vms",
        "vmlist":env.backend+"/vmlist",
        "packages":env.backend+"/packages",
        "ns":env.backend+"/namespaces",
        "db":env.backend+"/repository",
        "search": env.backend+"/packages/search",
        "profile": env.backend+"/user/profile",
        "installation": env.backend+"/installations"
    })

    env.user_agent = "ztc/"+version


add_init(init_cfg,prio=0)


    # ### TODO mactchdb true and parse board infomations
    # dev_list = _dsc.run_one(matchdb=False)
    # if uid in dev_list:
    #     #print(dev_list[uid])
    #     ### TODO load basic firmware and parse device informations (on_chip_id, type, etc.)
    #     dinfo = {
    #         "name": name,
    #         "on_chip_id": "123456789",
    #         "type": "flipnclick_sam3x",
    #         "category": "AT91SAM3X8E"
    #     }
    #     headers = {"Authorization": "Bearer "+env.token}
    #     try:
    #         res = zpost(url=dev_url, headers=headers, data=dinfo)
    #         #print(res.json())
    #         if res.json()["status"] == "success":
    #             info("Device",name,"created with uid:", res.json()["data"]["uid"])
    #             ### TODO save mongodb uid in sqlite db
    #         else:
    #             error("Error in device data:", res.json()["message"])
    #     except Exception as e:
    #         error("Can't create device entity")
    #         