import os
import os.path
import tempfile
import json
import shutil
import glob

__all__ = ["fs"]


class zfs():

    def __init__(self,tmpdir="."):
        self.tmpdir = self.apath(tmpdir)
        self.tempfiles=set()
        self.sep = os.sep

    # Temporary files
    def set_temp(self,tmpdir):
        self.tmpdir = self.apath(tmpdir)


    def get_tempfile(self,data):
        td = self.get_tempdir()
        fs.write_file(data,fs.path(td,"tmp.bin"))
        return fs.path(td,"tmp.bin")
        
    def del_tempfile(self,src):
        pass

    def get_tempdir(self):
        return tempfile.mkdtemp(dir=self.tmpdir)

    def del_tempdir(self,tmp):
        fs.rmtree(tmp)

    def get_json(self,src):
        with open(src,"r") as ff:
            return json.load(ff)

    def set_json(self,js,dst):
        with open(dst,"w") as ff:
            json.dump(js,ff,indent=4,sort_keys=True)

    def write_file(self,data,dst):
        if isinstance(data,str):
            d="w"
        else:
            d="wb"
        with open(dst,"wb") as ff:
            ff.write(data)

    def rmtree(self,dst):
        shutil.rmtree(dst)

    def copytree(self,src,dst):
        pass

    def copyfile(self,src,dst):
        shutil.copyfile(src,dst)

    def rmtree(self,dst):
        pass


    def mergetree(self,src,dst):
        pass

    def untarxz(self,src,dst):
        pass

    def tarxz(self,src,dst):
        pass

    def path(self,*args):
        return os.path.normpath(os.path.join(*args))

    def apath(self,path):
        return os.path.normpath(os.path.abspath(os.path.realpath(path)))

    def homedir(self):
        return self.apath(os.path.expanduser("~"))

    def basename(self,path):
        return os.path.basename(os.path.normpath(path))

    def dirname(self,path):
        return os.path.dirname(os.path.normpath(path))

    def split(self,path):
        return os.path.split(os.path.normpath(path))

    def glob(self,path,pattern):
        return glob.glob(fs.path(path,pattern))

    def exists(self,path):
        return os.path.exists(path)

    def isfile(self,path):
        return os.path.isfile(path)

    def isdir(self,path):
        return os.path.isdir(path)

    def stat(self,path):
        return os.stat(path)

    def dirs(self,path):
        root,dirnames,files = next(os.walk(path))
        return [self.path(path,x) for x in dirnames]

    def writefile(self,path,data):
        with open(path,"w") as ff:
            ff.write(data)

    def readfile(self,path,param=""):
        with open(path,"r"+param) as ff:
            return ff.read()

    def readlines(self,path):
        with open(path) as ff:
            return ff.readlines()

    def makedirs(self,dirs):
        if isinstance(dirs,str):
            os.makedirs(dirs,exist_ok=True)
        else:
            for d in dirs:
                os.makedirs(d,exist_ok=True)




fs=zfs()