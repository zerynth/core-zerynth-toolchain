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
            if fs.basename(tooldir) in ["browser","newbrowser","newpython"]:
                # ignore some sys packages
                continue
            print("Checking",tooldir)
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

    def get_vms(self,target):
        vms = {}
        for d in fs.dirs(env.vms):
            vmtarget = fs.basename(d)
            for r in fs.dirs(fs.path(env.vms,d)):
                vmfs = fs.glob(fs.path(env.vms,d,r),"*.vm")
                for vmf in vmfs:
                    vmbf = fs.basename(vmf)
                    rpos = vmbf.rfind("_") #rtos
                    hpos = vmbf.rfind("_",0,rpos-1) #hash
                    vpos = vmbf.rfind("_",0,hpos-1) #version
                    vmrtos = vmbf[rpos+1:-3]
                    vmhash = vmbf[hpos+1:rpos]
                    vmversion = vmbf[vpos+1:hpos]
                    vmuid = vmbf[0:vpos] #TODO: add check
                    
                    if target and vmtarget==target:
                        vms[vmuid]=vmf
                    elif not target:
                        vms[vmuid]=vmf
        return vms

    def _parse_order(self,path):
        order = fs.readfile(fs.path(path,"order.txt"))
        lines = order.split("\n")
        stack = []
        rs = []
        for line in lines:
            line = line.strip()
            if not line or len(line)<4 or line.startswith(";"):
                continue
            pos = line.count("#")
            if pos>0:
                label = line[pos:]
                while (len(stack)>=(pos)): stack.pop()
                stack.append(label)
            else:
                try:
                    ex = {
                        "tag":list(stack),
                        "name":line.replace("_"," "),
                        "path":fs.path(path,line),
                        "desc":fs.readfile(fs.path(path,line,"project.md")),
                        "code":fs.readfile(fs.path(path,line,"main.py")),
                    }
                    rs.append(ex)
                except:
                    pass
        return rs


    def _get_examples(self,path):
        return self._parse_order(path)
        
    def get_examples(self):
        exs = {}
        exr = []
        srcs = [fs.path(env.stdlib,"examples")]
        repos = fs.dirs(env.libs)
        if "official" in repos: #put official on top
            repos.remove("official")
            repos = ["official"]+repos
        for repo in repos:
            nms = fs.dirs(repo)
            for nm in nms:
                libs = fs.dirs(nm)
                for lib in libs:
                    srcs.append(fs.path(lib,"examples"))
        for exlib in srcs:
            if fs.exists(exlib):
                ee = self._get_examples(exlib)
                exr.extend(ee)
        return exr



#fs.set_json(rj["data"], fs.path(vmpath,uid+"_"+version+"_"+rj["data"]["hash_features"]+"_"+rj["data"]["rtos"]+".vm"))


tools = Tools()


add_init(tools.init)
