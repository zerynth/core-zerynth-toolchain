import os
import os.path
import tempfile
import json
import shutil
from .cfg import *

__all__ = ["fs"]


class zfs():

    def __init__(self,tmpdir="."):
        self.tmpdir = self.apath(tmpdir)
        self.tempfiles=set()

    # Temporary files
    def set_temp(self,tmpdir):
        self.tmpdir = self.apath(tmpdir)


    def get_tempfile(self):
        pass

    def del_tempfile(self):
        pass

    def get_json(self,src):
        with open(src,"r") as ff:
            return json.load(ff)

    def set_json(self,js,dst):
        with open(dst,"w") as ff:
            json.dump(js,ff,indent=4,sort_keys=True)

    def write_file(self,data,dst):
        with open(dst,"w") as ff:
            ff.write(data)

    def rmtree(self,dst, is_windows):
        ####TODO implement for windows
        shutil.rmtree(dst)

    def copytree(self,src,dst):
        pass

    def mergetree(self,src,dst):
        pass

    def untarxz(self,src,dst):
        pass

    def tarxz(self,src,dst):
        pass

    def path(self,*args):
        return os.path.join(*args)



    def apath(self,path):
        return os.path.abspath(os.path.realpath(path))

    def homedir(self):
        return self.apath(os.path.expanduser("~"))

    def dirs(self,path):
        root,dirnames,files = next(os.walk(path))
        return [self.path(path,x) for x in dirnames]

    def makedirs(self,dirs):
        if isinstance(dirs,str):
            os.makedirs(dirs,exist_ok=True)
        else:
            for d in dirs:
                os.makedirs(d,exist_ok=True)

    def file_exists(self, path):
        if isinstance(path, str):
            return os.path.isfile(path)
        return False

fs=zfs()