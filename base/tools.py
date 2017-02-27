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
            try:
                pkg = fs.get_json(fs.path(tooldir,"package.json"))
                toolname = pkg.get("tool")
                pkg = pkg["sys"]
            except Exception as e:
                warning("Can't load tool",tooldir)
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

    def get_vm(self,vmuid,version,chipid,target):
        vmpath = fs.path(env.vms,target,chipid)
        vmfs = fs.glob(vmpath,"*.vm")
        vm = None
        for vmf in vmfs:
            vmm = fs.basename(vmf)
            if vmm.startswith(vmuid+"_"+version+"_"):
                vm=vmf
        return vm

    def get_vm_by_uid(self,vmuid):
        #for root,dirnames,files in os.walk(fs.path(env.vms)):
        for target in fs.dirs(env.vms):
            for chid in fs.dirs(fs.path(env.vms,target)):
                for ff in fs.files(fs.path(env.vms,target,chid)):
                    path_splitted = ff.split('/')
                    ff_ = fs.basename(ff)
                    if ff_.startswith(vmuid+"_"):
                        return fs.path(ff)
        return None

    def get_vms(self,target,chipid=None,full_info=False):
        vms = {}
        targetpath = fs.path(env.vms,target)
        if not fs.exists(targetpath):
            return vms
        for chid in fs.dirs(targetpath):
            chid=fs.basename(chid)
            if chipid and chipid!=chid:
                continue
            vmfs = fs.glob(fs.path(targetpath,chid),"*.vm")
            for vmf in vmfs:
                vmbf = fs.basename(vmf)
                rpos = vmbf.rfind("_") #rtos
                hpos = vmbf.rfind("_",0,rpos-1) #hash
                vpos = vmbf.rfind("_",0,hpos-1) #version
                vmrtos = vmbf[rpos+1:-3]
                vmhash = vmbf[hpos+1:rpos]
                vmversion = vmbf[vpos+1:hpos]
                vmuid = vmbf[0:vpos] #TODO: add check
                if full_info:
                    vms[vmuid]=(vmf,vmversion,vmrtos,vmhash)
                else:
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
        srcs = [(fs.path(env.stdlib,"examples"),"core.zerynth.stdlib")]
        repos = fs.dirs(env.libs)
        if "official" in repos: #put official on top
            repos.remove("official")
            repos = ["official"]+repos
        for repo in repos:
            nms = fs.dirs(repo)
            for nm in nms:
                libs = fs.dirs(nm)
                for lib in libs:
                    srcs.append((fs.path(lib,"examples"),"lib."+fs.basename(nm)+"."+fs.basename(lib)))
        for exlib,lib in srcs:
            if fs.exists(exlib):
                ee = self._get_examples(exlib)
                for eee in ee:
                    eee["lib"]=lib
                exr.extend(ee)
        return exr

    def get_devices(self):
        bdirs = fs.dirs(env.devices)
        for bdir in bdirs:
            try:
                bj = fs.get_json(fs.path(bdir,"device.json"))
                bj["path"] = bdir
                yield bj
            except Exception as e:
                warning(e)

    def get_modules(self):
        res = {}
        # libraries
        rdirs = fs.dirs(env.libs)
        for r in rdirs:
            repo = fs.basename(r)
            nsdirs = fs.dirs(r)
            for ns in nsdirs:
                namespace = fs.basename(ns)
                lbdirs = fs.dirs(ns)
                for l in lbdirs:
                    lib = fs.basename(l)
                    if repo=="official":
                        if namespace=="zerynth":
                            module = lib
                        else:
                            module = namespace+"."+lib
                    else:
                        module = repo+"."+namespace+"."+lib
                    imports = []
                    for f in fs.files(l):
                        fl = fs.basename(f)
                        if fl.endswith(".py") and fl!="main.py":
                            imports.append(fl[0:-3])
                    res[module]=imports
        return res

    def get_vhal(self):
        vhal = {}
        arch_dirs = fs.dirs(env.vhal)
        for ad in arch_dirs:
            fmdirs = fs.dirs(ad)
            for fm in fmdirs:
                vhal_file = fs.path(fm,"vhal.json")
                if fs.exists(vhal_file):
                    vj = fs.get_json(vhal_file)
                    vhal.update(vj)
        return vhal




#fs.set_json(rj["data"], fs.path(vmpath,uid+"_"+version+"_"+rj["data"]["hash_features"]+"_"+rj["data"]["rtos"]+".vm"))


tools = Tools()


add_init(tools.init)
