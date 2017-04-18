import os
import os.path
import tempfile
import json
import shutil
import tarfile
import hashlib
import sys

from .cfg import *
import glob

__all__ = ["fs"]


class zfs():


    def __init__(self,tmpdir="."):
        self.tmpdir = self.apath(tmpdir)
        self.tempfiles=set()
        self.sep = os.sep
        # fix misnaming -_-
        self.read_file = self.readfile

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

    def get_hashdir(self,path):
        hh = hashlib.md5()
        hh.update(bytes(path,"utf-8"))
        pth = self.path(self.tmpdir,hh.hexdigest())
        self.rmtree(pth)
        self.makedirs(pth)
        return pth

    def get_json(self,src):
        with open(src,"r",encoding="utf8") as ff:
            return json.load(ff)

    def set_json(self,js,dst):
        with open(dst,"w",encoding="utf8") as ff:
            json.dump(js,ff,indent=4,sort_keys=True)

    def is_dir(self,src):
        return os.path.isdir(src)

    def rmtree(self,dst):
        try:
            if not fs.exists(dst):
                return
            shutil.rmtree(dst)
        except Exception as e:
            print(e)
            for path, dirs, files in os.walk(dst):
                for file in files:
                    try:
                        os.remove(os.path.join(path, file))
                    except Exception as e:
                        print("Warning: can't remove file :", file, "error: ", e)

    def rm_file(self, dst):
        try:
            os.remove(os.path.join(dst))
        except Exception as e:
            print("Warning: can't remove file :", dst, "error: ", e)

    def copytree(self,src,dst):
        shutil.rmtree(dst,ignore_errors=True)
        try:
            shutil.copytree(src,dst,ignore_dangling_symlinks=True)
        except:
            pass
            #TODO: copy by walking

    def copyfile(self,src,dst):
        shutil.copyfile(src,dst)

    # Must be used in board support files only!
    def copyfile2(self,src,dst):
        if sys.platform.startswith("win"):
            # some block devices don't work with shutil in some windows configurations (e.g. st_nucleo) -_-
            # can't use proc.py with pipes...use os.system -_-
            os.system("echo f | xcopy /f /y \"%s\" \"%s\""%(src,dst))
        else:
            shutil.copyfile(src,dst)

    def file_hash(self,dst):
        hh = hashlib.md5()
        with open(dst,"rb") as ff:
            hh.update(ff.read())
        return hh.hexdigest()

    def untarxz(self,src,dst):
        zp = tarfile.open(src,"r:xz")
        zp.extractall(dst)
        zp.close()

    def mergetree(self,src,dst):
        pass

    def __tarfn(self,obj,original, archive):
        obj.add(original,arcname=archive)


    def __zipdir(self,path, zip, fn, rmpath):
        for root, dirs, files in os.walk(path):
            for file in files:
                if "/." in root:
                    continue
                elif file.startswith("."):
                    continue
                #print(os.path.join(root, file),"=>",os.path.join(root.replace(rmpath,"").strip("/"),file))
                fn(zip,os.path.join(root, file),os.path.join(root.replace(rmpath,"").strip("/"),file))


    def tarxz(self,src,dst):
        tar = tarfile.open(dst,"w:xz",preset=9)
        self.__zipdir(src,tar,self.__tarfn,src)
        tar.close()


    def unique_paths(self,pths):
        pths = list(pths)
        res = []
        dups = set()
        for i in range(len(pths)):
            pi = pths[i]
            for j in range(i+1,len(pths)):
                if j in dups:
                    continue # skip checked
                pj = pths[j]
                if pi==pj or os.path.samefile(pi,pj):
                    dups.add(j)
            if i not in dups:
                res.append(pi)
        return res

    def path(self,*args):
        return os.path.normpath(os.path.join(*args))

    def apath(self,path):
        return os.path.normpath(os.path.abspath(os.path.realpath(path)))

    def rpath(self,path,parent):
        return os.path.relpath(path,parent)

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

    def files(self,path):
        root,dirnames,files = next(os.walk(path))
        return [self.path(path,x) for x in files]

    def write_file(self,data,dst):
        if isinstance(data,str):
            d="w"
            with open(dst,d,encoding="utf8") as ff:
                ff.write(data)
        else:
            d="wb"
            with open(dst,d) as ff:
                ff.write(data)
        

    def readfile(self,path,param=""):
        if param:
            with open(path,"r"+param) as ff:
                return ff.read()
        else:
            with open(path,"r",encoding="utf8") as ff:
                return ff.read()

    def readlines(self,path):
        with open(path,encoding="utf8") as ff:
            return ff.readlines()
 
    def makedirs(self,dirs):
        if isinstance(dirs,str):
            os.makedirs(dirs,exist_ok=True)
        else:
            for d in dirs:
                os.makedirs(d,exist_ok=True)

    def rm_readonly(self, func, path):
        try:
            if not os.path.exists(path):
                return
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print("ERROR in rmtree %s"%str(e))

    # def remove_readonly_no_output(self, func, path, excinfo):
    #     #used to hide the whooosh bug when updating the index in, guess.., windows -_-
    #     try:
    #         if not os.path.exists(path):
    #             return
    #         os.chmod(path, stat.S_IWRITE)
    #         func(path)
    #     except Exception as e:
    #         pass

fs=zfs()

