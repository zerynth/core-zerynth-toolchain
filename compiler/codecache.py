from base import *
import hashlib

class CodeCache():
    def __init__(self):
        self.basepath = fs.path(env.tmp,"native_cache")
        self.cache = {}
        self.target=""

    def set_target(self,prefix,target,defs=[]):
        sdf=""
        for x in sorted(defs):
            sdf=sdf+str(x)+"&&"
        self.target=target
        self.hash=target+"::"+sdf
        hasher = hashlib.sha1()
        hasher.update(bytes(self.hash,"utf-8"))
        self.path=fs.path(self.basepath,hasher.hexdigest()+"_"+prefix.replace("\\","_").replace("/","_").replace(":","_")+"_"+target)
        fs.makedirs(self.path)
        try:
            self.cache=fs.get_json(fs.path(self.path,".cache"))
        except:
            self.cache={}

    def add_object(self,cfile,ofile,hfiles=[]):
        statinfo = fs.stat(cfile)
        ofilename = fs.basename(ofile)
        cfilename = fs.path(self.path,ofilename)
        self.cache[self.hash+cfile]={
            "mtime":statinfo.st_mtime,
            "ofile":cfilename,
            "headers": {k:fs.stat(k).st_mtime for k in hfiles}
        }
        fs.copyfile(ofile,cfilename)
        fs.set_json(self.cache,fs.path(self.path,".cache"))
        #print("CACHE added",cfile,"=>",self.cache[cfile])

    def has_object(self,cfile):
        hfile = self.hash+cfile
        if hfile in self.cache:
            file = self.cache[hfile]
            #print(cfile,"=>",self.cache[cfile],"==",statinfo.st_mtime)
            if fs.stat(cfile).st_mtime!=file["mtime"]:
                #file has changed
                return False
            else:
                #check all headers
                for h,t in file["headers"].items():
                    if fs.stat(h).st_mtime!=t:
                        return False
                return file["ofile"]
        return False