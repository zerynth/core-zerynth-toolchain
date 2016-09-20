import sys
import sqlite3
from .base import *
from .fs import *

__all__=['env']

class Var():
    def __init__(self, _dict={}):
        self._v=dict(_dict)
        for k,v in _dict.items():
            if isinstance(v,dict):
                self._v[k] = Var(v)
            else:
                self._v[k] = v

    def __getattr__(self,attr):
        return self._v[attr]


class Environment():
    
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

    def load_dbs(self,cfgdir,dbname):
        try:
            #js = fs.get_json(fs.path(cfgdir,dbname))
            self._dbs_cfgdir=cfgdir
            self._dbs_dbname=dbname
            self._dbs = sqlite3.connect(fs.path(cfgdir,dbname),check_same_thread=False)
            self._dbs.execute("CREATE TABLE IF NOT EXISTS aliases (alias TEXT PRIMARY KEY, uid TEXT, shortname TEXT, name TEXT)")
            self._dbs.execute("CREATE UNIQUE INDEX IF NOT EXISTS aliases_idx ON aliases(alias)")
            self._dbs.execute("CREATE UNIQUE INDEX IF NOT EXISTS uid_idx ON aliases(uid)")
        except Exception as e:
            self._dbs = None

    def save_dbs(self):
        try:
            self._dbs.commit()
        except Exception as e:
            critical("can't save configuration",exc=e)

    def get_dev(self,key):
        res = {}
        for row in self._dbs.execute("select * from aliases where alias=? or uid=?",(key,key)):
            res[row[0]]=Var({"alias":row[0],"uid":row[1],"target":var[2],"name":var[3]})
        return res
    


    def put_dev(self,dev):
        if not isinstance(dev,Var):
            dev = Var(dev)
        self._dbs.execute("insert or replace into aliases values(?,?,?,?)",(dev.alias,dev.uid,dev.target,dev.name))
        self._dbs.commit()

    def del_dev(self,dev):
        self._dbs.execute("delete from aliases where alias=?",(dev.alias,))
        self._dbs.commit()


env=Environment()


# ####
#     .Zerynth/
#         cfg/
#             devdb/
#         workspace/
#         sys/
#         tmp/
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

    # main directories
    zdir = "Zerynth" if env.is_windows() else ".Zerynth"
    env.home      = fs.path(fs.homedir(),zdir)
    env.cfg       = fs.path(env.home,"cfg")
    env.devdb     = fs.path(env.home,"cfg","devdb")
    env.tmp       = fs.path(env.home,"tmp")
    env.cache     = fs.path(env.tmp,"cache")
    env.sys       = fs.path(env.home,"sys")
    env.workspace = fs.path(env.home,"workspace")

    # load configuration
    env.load(env.cfg)
    env.load_dbs(env.cfg,"db.json")
    version = env.var.version

    # dist directories
    env.ztc       = fs.path(env.home,"dist",version,"ztc")
    env.libs      = fs.path(env.home,"dist",version,"libs")
    env.nest      = fs.path(env.home,"dist",version,"nest")
    env.stdlib    = fs.path(env.home,"dist",version,"stdlib")
    env.vhal      = fs.path(env.home,"dist",version,"vhal")
    env.studio    = fs.path(env.home,"dist",version,"studio")
    env.docs      = fs.path(env.home,"dist",version,"docs")
    env.examples  = fs.path(env.home,"dist",version,"examples")
    env.devices    = fs.path(env.home,"dist",version,"devices")

    # set global temp dir
    fs.set_temp(env.tmp)

    # create dirs
    fs.makedirs(env.dirs())

add_init(init_cfg,prio=0)