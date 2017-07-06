import sys
import sqlite3
from .base import *
from .fs import *
import json
import base64
import os
import uuid

__all__=['env','Var','decode_base64']

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

    def save(self,cfgdir=None,version=None):
        try:
            if not cfgdir:
                cfgdir=self.cfg
            dd = self.var.to_dict()
            if version:
                dd["version"]=version
            js = fs.set_json(dd,fs.path(cfgdir,"config.json"))
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
            self._dbs.execute("CREATE TABLE IF NOT EXISTS linked (alias TEXT PRIMARY KEY,uid TEXT,target TEXT, name TEXT, chipid TEXT, remote_id TEXT, classname TEXT)")
            self._dbs.execute("CREATE UNIQUE INDEX IF NOT EXISTS linked_a_idx ON linked(alias)")
            self._dbs.execute("CREATE INDEX IF NOT EXISTS linked_t_idx ON linked(target)")
            self._dbs.execute("CREATE INDEX IF NOT EXISTS linked_c_idx ON linked(chipid)")
            
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

    def get_linked_devs(self,target):
        res = {}
        for row in self._dbs.execute("select * from linked where target=?",(target,)):
            res[row[0]]=Var({"alias":row[0],"uid":row[1],"target":row[2],"name":row[3],"chipid":row[4],"remote_id":row[5],"classname":row[6]})
        return res

    def get_dev_by_alias(self,alias):
        res = []
        for row in self._dbs.execute("select * from aliases where alias like '"+alias+"%'"):
            res.append(Var({"alias":row[0],"uid":row[1],"target":row[2],"name":row[3],"chipid":row[4],"remote_id":row[5],"classname":row[6]}))
        if not res: #if nothing in primary db, search linked db
            for row in self._dbs.execute("select * from linked where alias like '"+alias+"%'"):
                res.append(Var({"alias":row[0],"uid":row[1],"target":row[2],"name":row[3],"chipid":row[4],"remote_id":row[5],"classname":row[6]}))
        return res

    def put_dev(self,dev,linked=False):
        if not isinstance(dev,Var):
            dev = Var(dev)
        if not linked:
            self._dbs.execute("insert or replace into aliases values(?,?,?,?,?,?,?)",(dev.alias,dev.uid,dev.target,dev.name,dev.chipid,dev.remote_id,dev.classname))
        else:
            dev.alias = str(dev.target)+":"+str(dev.chipid)
            dev.name = dev.name+" ("+str(dev.remote_id)+")"
            self._dbs.execute("insert or replace into linked values(?,?,?,?,?,?,?)",(dev.alias,str(uuid.uuid4()),dev.target,dev.name,dev.chipid,dev.remote_id,dev.classname))
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
        fs.makedirs(self.idb_dir(distpath))


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

    def set_token(self,rawtoken,toktype=None):
        pl = rawtoken.split(".")[1]
        js = json.loads(decode_base64(pl).decode("utf-8"))
        token = {
            "token":rawtoken,
            "expires":js["exp"],
            "type": toktype
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

    testmode = int(os.environ.get("ZERYNTH_TESTMODE",0))
    # main directories TODO: change zdir to official zdir
    if testmode == 2:
        # special testing mode
        zdir = "zerynth2_test" if env.is_windows() else ".zerynth2_test"
    else:
        zdir = "zerynth2" if env.is_windows() else ".zerynth2"
    env.home      = fs.path(fs.homedir(),zdir)
    env.cfg       = fs.path(env.home,"cfg")
    env.tmp       = fs.path(env.home,"tmp")
    env.sys       = fs.path(env.home,"sys")
    env.vms       = fs.path(env.home,"vms")
    env.edb       = fs.path(env.home,"cfg","edb")
    env.zdb       = fs.path(env.home,"cfg","zdb")
    

    # load configuration
    env.load(env.cfg)
    env.load_dbs(env.cfg,"devices.db")
    #env.load_zpack_db(env.zdb,"packages.db")
    #env.load_ipack_db(env.idb,"packages.db")
    version = env.var.version
    if testmode==1:
        # local
        env.git_url   = os.environ.get("ZERYNTH_GIT_URL","http://localhost/git")
        env.backend   = os.environ.get("ZERYNTH_BACKEND_URL","http://localhost/v1")
        env.connector = os.environ.get("ZERYNTH_ADM_URL","http://localhost/v1")
    elif testmode==2:
        # CI
        env.git_url   = os.environ.get("ZERYNTH_GIT_URL","https://test.zerynth.com/git")
        env.backend   = os.environ.get("ZERYNTH_BACKEND_URL","https://test.zerynth.com/v1")
        env.connector = os.environ.get("ZERYNTH_ADM_URL","http://test.zerynth.com:7700" )
    else:
        # remote
        env.git_url ="https://backend.zerynth.com/git"
        env.backend="https://backend.zerynth.com/v1"
        env.connector="https://api.zerynth.com/v1"

    # dist directories
    env.dist      = fs.path(env.home,"dist",version)
    env.ztc       = fs.path(env.home,"dist",version,"ztc")
    env.libs      = fs.path(env.home,"dist",version,"libs")
    env.nest      = fs.path(env.home,"dist",version,"nest")
    env.stdlib    = fs.path(env.home,"dist",version,"stdlib")
    env.vhal      = fs.path(env.home,"dist",version,"vhal") 
    env.studio    = fs.path(env.home,"dist",version,"studio")
    env.docs      = fs.path(env.home,"dist",version,"docs")
    env.examples  = fs.path(env.home,"dist",version,"examples")
    env.devices    = fs.path(env.home,"dist",version,"devices")
    env.things    = fs.path(env.home,"dist",version,"things")
    env.idb       = fs.path(env.home,"dist",version,"idb")

    env.dist_dir = lambda x: fs.path(env.home,"dist",x)
    env.ztc_dir = lambda x: fs.path(x,"ztc")
    env.lib_dir = lambda x: fs.path(x,"libs")
    env.stdlib_dir = lambda x: fs.path(x,"stdlib")
    env.studio_dir = lambda x: fs.path(x,"studio")
    env.vhal_dir = lambda x: fs.path(x,"vhal")
    env.devices_dir = lambda x: fs.path(x,"devices")
    env.things_dir = lambda x: fs.path(x,"things")
    env.docs_dir = lambda x: fs.path(x,"docs")
    env.examples_dir = lambda x: fs.path(x,"examples")
    env.idb_dir = lambda x: fs.path(x,"idb")


    # set global temp dir
    fs.set_temp(env.tmp)

    # create dirs
    fs.makedirs(env.dirs())

    # backend & api
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
        "installation": env.backend+"/installations",
        "user": env.backend+"/user"
    })

    env.admfile = fs.path(env.cfg,"adm.json")
    if fs.exists(env.admfile):
        try:
            admcfg = fs.get_json(env.admfile)
            if "url" in admcfg:
                env.connector=admcfg["url"]
        except:
            warning("Bad json in",env.admfile)

    env.thing = Var({
        "devices":env.connector+"/devices",
        "groups":env.connector+"/groups",
        "templates":env.connector+"/templates",
        "template":env.connector+"/templates/%s",
        "group":env.connector+"/groups/%s",
        "calls":env.connector+"/devices/%s/call",
        "config":env.connector+"/devices/%s/config",
        "ota":env.connector+"/devices/%s/ota",
        "monitor":env.connector.replace("https://","wss://",1).replace("http://","ws://",1)+"/monitor"
    })

    env.user_agent = "ztc/"+version

    env.proxies=None
    env.proxyfile = fs.path(env.cfg,"proxy.json")
    if fs.exists(env.proxyfile):
        try:
            env.proxies = fs.get_json(env.proxyfile)
        except:
            warning("Bad json in",env.proxyfile)

    #set minimum compatible vm version
    env.min_vm_dep="r2.0.9"

add_init(init_cfg,prio=0)
