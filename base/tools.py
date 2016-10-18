from .base import *
from .fs import *
from .cfg import *

__all__ = ["tools"]



class Tools():
    def __init__(self):
        self.tools = {}

    def init(self):
        #register platform tools
        if env.is_windows():
            self.tools["stty"]="mode"
        elif env.is_linux():
            self.tools["stty"]="/bin/stty -F"
        else:
            self.tools["stty"]="/bin/stty -f"
    
        for tooldir in fs.dirs(env.sys):
            try:
                pkg = fs.get_json(fs.path(tooldir,"package.json"))
                toolname = pkg.get("tool")
                pkg = pkg["sys"]
            except Exception as e:
                warning("Can't load tool",tooldir,err=True)
                continue
            if toolname:
                self.tools[toolname]={}
                addto = self.tools[toolname]
            else:
                addto = self.tools
            if isinstance(pkg,dict):
                for k,v in pkg.items():
                    addto[k]=fs.path(env.sys,tooldir,v)
            elif isinstance(pkg,list) or isinstance(pkg,tuple):
                for k,v in pkg:
                    addto[k]=fs.path(env.sys,tooldir,v)
            else:
                warning("Can't load tool info",tooldir,err=True)
        #print(self.tools)

    def __getattr__(self,attr):
        if attr in self.tools:
            return self.tools[attr]
        raise AttributeError

    def __getitem__(self,attr):
        if attr in self.tools:
            return self.tools[attr]
        raise KeyError

    def get_vms(self):
        vms = {}
        for d in fs.dirs(env.nest):
            vmfs = fs.glob(fs.path(env.nest,d),"*.vm")
            for vmf in vmfs:
                vmuid = vmf[-39:-3] #TODO: add check
                vms[vmuid]=vmf
        return vms



tools = Tools()


add_init(tools.init)
