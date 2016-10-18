from base import *
from .zversions import *

class Package():
    def __init__(self,var,uid):
        
        self.uid = uid
        self.fullname = var.fullname
        self.name = var.name
        self.description = var.description
        self.git_pointer = var.git_pointer
        self.type = var.type
        self.tag = var.tag
        self.authname = var.authname
        self.last_version = ZpmVersion(var.last_version)
        self.last_update = var.last_update

        self.dependencies = json.loads(var.dependencies)
        self.whatsnew = json.loads(var.whatsnew)
        
        self.rating = var.rating
        self.num_of_votes = var.num_of_votes
        self.num_of_downloads = var.num_of_downloads
        self.keywords = var.keywords
        try:
            self.keywords = json.loads(self.keywords)
        except:
            self.keywords=[]
        # self.installed = 0
        # self.enabled = False
        self.versions = [ZpmVersion(y) for y in json.loads(var.versions)]
        self.versions.sort()
        # if self.type=="sys":
        #     self.platform = self.json["versions"][str(self.versions[0])].get("platform","")
            
    def to_var(self):
        return {
            "uid":self.uid,
            "fullname":self.fullname,
            "name":self.name,
            "description":self.description,
            "git_pointer":self.git_pointer,
            "type":self.type,
            "tag":self.tag,
            "authname":self.authname,
            "last_version":str(self.last_version),
            "dependencies": json.dumps(self.dependencies),
            "whatsnew": json.dumps(self.whatsnew),
            "rating":self.rating,
            "num_of_votes":self.num_of_votes,
            "num_of_downloads":self.num_of_downloads,
            # "installed": False if not self.installed else str(self.installed),
            # "enabled":self.enabled,
            "versions":json.dumps([str(v) for v in self.versions]),
            "keywords":json.dumps(self.keywords),
            "last_update":self.last_update,
        }
    def to_dict(self):
        return {
            "uid":self.uid,
            "fullname":self.fullname,
            "name":self.name,
            "description":self.description,
            "git_pointer":self.git_pointer,
            "type":self.type,
            "tag":self.tag,
            "authname":self.authname,
            "last_version":str(self.last_version),
            "dependencies": self.dependencies,
            "whatsnew": self.whatsnew,
            "rating":self.rating,
            "num_of_votes":self.num_of_votes,
            "num_of_downloads":self.num_of_downloads,
            # "installed": False if not self.installed else str(self.installed),
            # "enabled":self.enabled,
            "versions":[str(v) for v in self.versions],
            "keywords":self.keywords,
            "last_update":self.last_update,
        }
    def to_row(self,version):
        return (self.uid,self.fullname,self.name,self.description,self.git_pointer,self.type,self.tag,self.authname,self.last_version,self.dependencies,self.whatsnew,self.rating,self.num_of_votes,self.num_of_downloads,self.versions,self.keywords,self.last_update)
    def __str__(self):
        return json.dumps(self.to_dict(),sort_keys=True,indent=4)
    def is_sys(self):
        return self.type=="sys"
    def get_folders(self,version):
        res = {"test_localzpm":env.env}
        # testing = "" if not version.testing else "testing"
        # ctesting = "official" if not version.testing else "testing"
        # if self.namespace=="zerynth":
        #     # handle viper packages
        #     if self.type == "lib":
        #         res["examples"]=os.path.realpath(os.path.join(vconf.envdirs["examples"],self.tag,self.path))
        #         res["docs"]=os.path.realpath(os.path.join(vconf.envdirs["docs"],self.tag,self.path))
        #         res["path"]=os.path.realpath(os.path.join(vconf.envdirs["libs"],self.tag,self.path))
        #     elif self.type == "core":
        #         res["path"]=os.path.realpath(os.path.join(vconf.envdirs["root"],"official",self.path))
        #         res["docs"]=os.path.realpath(os.path.join(vconf.envdirs["root"],"official",self.path,"docs","html"))
        #     elif self.type == "sys":
        #         res["path"]=os.path.realpath(os.path.join(vconf.envdirs["sys"],self.get_json_field("targetdir",version)))
        #     elif self.type == "board":
        #         res["path"]=os.path.realpath(os.path.join(vconf.envdirs["root"],"official","boards",self.path))
        #         res["docs"]=os.path.realpath(os.path.join(vconf.envdirs["root"],"official","boards",self.path,"docs","html"))
        #     elif self.type == "vhal":
        #         res["path"]=os.path.realpath(os.path.join(vconf.envdirs["root"],"official","vhal",self.path))
        #     elif self.type == "vm":
        #         res["path"]=os.path.realpath(os.path.join(vconf.envdirs["root"],"official","nest",self.path))
        # else:
        #     # it's a library, not from viper namespace
        #     if self.type == "lib":
        #         res["examples"]=os.path.realpath(os.path.join(vconf.envdirs["examples"],self.tag,self.namespace,self.path))
        #         res["docs"]=os.path.realpath(os.path.join(vconf.envdirs["docs"],self.tag,self.namespace,self.path))
        #         res["path"]=os.path.realpath(os.path.join(vconf.envdirs["libs"],self.tag,self.namespace,self.path))
        return res