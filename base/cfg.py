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
    
    def __init__(self):
        self.commands={}

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
            self._dbs.execute("CREATE TABLE IF NOT EXISTS aliases (alias TEXT PRIMARY KEY, uid TEXT, target TEXT, name TEXT)")
            self._dbs.execute("CREATE UNIQUE INDEX IF NOT EXISTS aliases_idx ON aliases(alias)")
            self._dbs.execute("CREATE UNIQUE INDEX IF NOT EXISTS uid_idx ON aliases(uid)")
        except Exception as e:
            self._dbs = None

    def load_pack_db(self,cfgdir,dbname):
        try:
            self._pack_db_cfgdir=cfgdir
            self._pack_db_dbname=dbname
            self._pack_db = sqlite3.connect(fs.path(cfgdir,dbname),check_same_thread=False)
            self._pack_db.execute("create table IF NOT EXISTS packages(uid TEXT PRIMARY KEY, fullname TEXT, type TEXT, tag TEXT, authname TEXT, last_version TEXT, dependencies TEXT, whatsnew TEXT, rating REAL, num_of_votes INTEGER, num_of_downloads INTEGER, last_update TEXT)")
            self._pack_db.execute("create unique index IF NOT EXISTS packagenames on packages(fullname)")
        except Exception as e:
            self._pack_db = None

    def save_dbs(self):
        try:
            self._dbs.commit()
        except Exception as e:
            critical("can't save configuration",exc=e)

    def save_pack_db(self):
        try:
            self._pack_db.commit()
        except Exception as e:
            critical("can't save configuration",exc=e)

    def get_dev(self,key):
        res = {}
        for row in self._dbs.execute("select * from aliases where alias=? or uid=?",(key,key)):
            res[row[0]]=Var({"alias":row[0],"uid":row[1],"target":row[2],"name":row[3]})
        return res

    def get_pack(self,fullname):
        res = {}
        for row in self._pack_db.execute("select * from packages where fullname=?",(fullname)):
            res[row[0]]=Var({
                    "uid":row[0],
                    "fullname":row[1],
                    "type":row[2],
                    "tag":row[3],
                    "authname":row[4],
                    "last_version":row[5],
                    "dependencies":row[6], 
                    "whatsnew":row[7],
                    "rating":row[8],
                    "num_of_votes":row[9],
                    "num_of_downloads":row[10],
                    "last_update":row[11]
                    })
        return res

    def put_dev(self,dev):
        if not isinstance(dev,Var):
            dev = Var(dev)
        self._dbs.execute("insert or replace into aliases values(?,?,?,?)",(dev.alias,dev.uid,dev.target,dev.name))
        self._dbs.commit()

    def put_pack(self,pack):
        if not isinstance(pack,Var):
            pack = Var(pack)
        self._pack_db.execute("insert or replace into packages values(?,?,?,?,?,?,?,?,?,?,?,?)",(pack.uid, pack.fullname, pack.type, pack.tag, pack.authname, pack.last_version, pack.dependencies, pack.whatsnew, pack.rating, pack.num_of_votes, pack.num_of_downloads, pack.last_update))
        self._pack_db.commit()

    def del_dev(self,dev):
        self._dbs.execute("delete from aliases where alias=?",(dev.alias,))
        self._dbs.commit()

    def add_command(self,cmdname,cmdvalue):
        self.commands[cmdname]=cmdvalue

    def get_command(self,cmdname):
        return self.commands.get(cmdname)


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
    env.vms       = fs.path(env.home,"vms")
    env.edb       = fs.path(env.home,"cfg","edb")
    env.zdb       = fs.path(env.home,"cfg","zdb")

    # load configuration
    env.load(env.cfg)
    env.load_dbs(env.cfg,"devices.db")
    env.load_pack_db(env.zdb,"packages.db")
    version = env.var.version
    env.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ6ZXJ5bnRoIiwidWlkIjoiMmo4dWVzNXJTTGFoSGRXX2VENnIwQSIsImV4cCI6MTQ3Njk2NzYwOCwiaWF0IjoxNDc0Mzc1NjA4LCJqdGkiOiJjVDZtRF9RMVF0Mld4MkJtYzVZNlR3In0.UanEyipdHxkoxpEvk9Eyg_PMS3C6lUsF7vGB4E9CkFg"
    env.git_url = "localhost/git/"

    # dist directories
    env.ztc       = fs.path(env.home,"dist",version,"ztc")
    env.libs      = fs.path(env.home,"dist",version,"libs")
    env.nest      = fs.path(env.home,"dist",version,"nest")
    env.stdlib    = fs.path(env.home,"dist",version,"stdlib")
    env.vhal      = fs.path(env.home,"dist",version,"vhal")
    env.studio    = fs.path(env.home,"dist",version,"studio")
    env.docs      = fs.path(env.home,"dist",version,"docs")
    env.examples  = fs.path(env.home,"dist",version,"examples")
    #env.devices    = fs.path(env.home,"dist",version,"devices")
    env.devices    = fs.path(fs.homedir(),"git","ZerynthBoards") #TODO: remove

    # set global temp dir
    fs.set_temp(env.tmp)

    # create dirs
    fs.makedirs(env.dirs())

add_init(init_cfg,prio=0)