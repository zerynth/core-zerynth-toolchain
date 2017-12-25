from base import *
from .zversions import *
import sqlite3
import json
import tarfile
import zlib
import lzma
import time
import requests

class Zpm():

    def __init__(self):
        pass

    def _download_package(self,fullname,version,patch="base",hash=None,callback=None):
        for attempt in range(6,20,6):
            try:
                outfile = fs.path(env.tmp,fullname+"-"+str(version)+".tar.xz")
                url = env.api.packages+"/"+fullname+"/"+str(version)+"/"+patch
                r = zgetraw(url)
                with open(outfile,"wb") as f:
                    fs.copyfileobj(r,f)
                if hash is not None:
                    hh = md5(outfile)
                    if hh!=hash:
                        # bad download!
                        continue
                return True
            except Exception as e:
                debug("download exception",str(e))
            debug("Attempt",str(attempt))
            time.sleep(attempt)
        return False


    def install(self,to_download,callback=None,offline=None):
        #download all packages from to_download list
        if not offline:
            self._clear_tmp_folder()
        for pp in sorted(to_download):
            pack = self.get_package(pp)
            vers = to_download[pp]
            print("==>",pp)
            if pack.type=="meta":
                continue # meta packages have no files
            if offline:
                info("Downloading", pack.fullname, vers)
            else:
                info("Downloading", pack.fullname, vers)
            res = self._download_package(pack, vers,callback,offline)
            if res is not True:
                fatal("Can't download package",pack.fullname,vers,"with error",res)

        core = to_download.get("meta.zerynth.core")
    
        if core:
            # need to create a new dist
            dpath = env.dist_dir(core)
            fs.copytree(env.dist,dpath)
            #delete any patches.json in new folder
            pthfile = fs.path(dpath,"patches.json")
            if fs.exists(pthfile):
                fs.rm_file(pthfile)
            #reload installed packages db
            self.load_ipack_db(env.idb_dir(dpath))
        else:
            # no dist change
            dpath = env.dist

        env.make_dist_dirs(dpath)
        # install all downloaded packages
        for pp in to_download:
            pack = self.get_package(pp)
            vers = to_download[pp]
            pack.file = fs.path(env.tmp, pack.fullname+"-"+str(vers)+".tar.xz")
            info("Installing",pack.fullname,vers)

            if pack.type=="meta":
                self._install_package(pack,vers)
            elif pack.type=="lib":
                self._install_lib(pack,vers,dpath)
            elif pack.type=="core":
                self._install_core(pack,vers,dpath)
            elif pack.type=="board":
                self._install_device(pack,vers,dpath)
            elif pack.type=="vhal":
                self._install_vhal(pack,vers,dpath)
            elif pack.type=="sys":
                self._install_sys(pack,vers,dpath)

        self._clear_tmp_folder()
        if core:
            env.save(version=core)
            if offline:
                # update patchfile for offline installations
                try:
                    fs.copyfile(fs.path(offline,"patches.json"),fs.path(dpath,"patches.json"))
                except:
                    warning("Can't copy patch file!")
            else:
                self.save_patch(dpath,core)
        return core

    def save_patch(self,path,version):
        try:
            fname = "patchbase-"+env.platform+".json"
            res = zget(url=env.patchurl+"/patches/"+version+"/"+fname,auth=False)
            if res.status_code == 200:
                npth = res.json()
                fs.set_json(npth,fs.path(path,"patches.json"))
            else:
                warning("No patches available for",version,[res.status_code])
                return
        except Exception as e:
            warning("Error while asking for patches",version,e)
            return
        

    def _install_lib(self,package,version,distpath):
        lib_src = fs.get_tempdir()
        fs.untarxz(package.file,lib_src)

        ex_src = fs.path(lib_src,"examples")
        doc_src = fs.path(lib_src,"docs")

        libsdir = env.lib_dir(distpath)
        flds = package.fullname.split(".")
        namespace = flds[1]
        name = flds[2]
        repo = package.repo
        lib_dst = fs.path(libsdir,repo,namespace,name)
        ex_dst =  fs.path(env.examples_dir(distpath), package.fullname)
        #doc_dst =  fs.path(env.docs_dir(distpath), package.fullname)

        fs.rmtree(doc_src)
        # clean dist directories
        fs.rmtree(lib_dst)
        fs.rmtree(ex_dst)
        info("    installing in",lib_dst)
        fs.copytree(lib_src,lib_dst)
        fs.del_tempdir(lib_src)

    def _install_sys(self,package,version,distpath):
        sys_src = fs.get_tempdir()
        fs.untarxz(package.file,sys_src)
        pk = fs.get_json(fs.path(sys_src,"package.json"))
        tdir = pk["targetdir"]
        
        if package.fullname.startswith("sys.zerynth.runtime-"):
            # treat runtime with care! change dst or try first, then change
            pass
        elif package.fullname.startswith("sys.zerynth.browser-"):
            # remove package.json, not needed as a tool and interfere with nw.js
            fs.rm_file(fs.path(sys_src,"package.json"))
        dst = fs.path(env.sys,tdir)
        info("    installing in",dst)
        fs.copytree(sys_src,dst)
        self._install_package(package,version)
        fs.del_tempdir(sys_src)

    def _install_vhal(self,package,version,distpath):
        vhal_src = fs.get_tempdir()
        fs.untarxz(package.file,vhal_src)
        pk = fs.get_json(fs.path(vhal_src,"package.json"))
        tdir = pk["targetdir"]
        dst = fs.path(env.vhal_dir(distpath),tdir)
        info("    installing in",dst)
        fs.copytree(vhal_src,dst)
        self._install_package(package,version)
        fs.del_tempdir(vhal_src)

    def _install_device(self,package,version,distpath):
        dev_dst = fs.path(env.devices_dir(distpath),package.fullname.split(".")[2])
        fs.rmtree(dev_dst)
        fs.makedirs(dev_dst)
        info("    installing in",dev_dst)
        fs.untarxz(package.file,dev_dst)
        self._install_package(package,version)


    def _install_core(self,package,version,distpath):
        if package.fullname=="core.zerynth.toolchain":
            dst = env.ztc_dir(distpath)
        elif package.fullname=="core.zerynth.studio":
            dst = env.studio_dir(distpath)
        elif package.fullname=="core.zerynth.stdlib":
            dst = env.stdlib_dir(distpath)
        else:
            # just in case
            dst = fs.path(distpath,package.fullname.split(".")[2])
        info("    installing in",dst)
        fs.rmtree(dst)
        # if package.fullname =="core.zerynth.docs":
        #     src = fs.get_tempdir()
        #     fs.untarxz(package.file,src)
        #     fs.copytree(fs.path(src,"docs","html"),dst)
        #     fs.del_tempdir(src)
        # else:
        fs.untarxz(package.file,dst)
        # if package.fullname=="core.zerynth.stdlib":
        #     #move examples
        #     edst = fs.path(env.examples_dir(distpath),package.fullname)
        #     esrc = fs.path(dst,"examples")
        #     fs.rmtree(edst)
        #     fs.copytree(esrc,edst)
        #     fs.rmtree(esrc)
        if package.fullname == "core.zerynth.studio":
            #change package.json for nw.js
            packjson = {
                          "name": "Zerynth Studio",
                          "main": "index.html",
                          "window": {
                            "frame": True,
                            "min_width": 800,
                            "min_height": 600
                          },
                          "version":env.var.version,
                          "user-agent":"ide/%ver/"+env.platform
                        }
            # no icon for mac, it's already in the browser
            if not env.is_mac():
                packjson["window"].update({"icon":"img/Logo512.png"})
            fs.set_json(packjson,fs.path(dst,"package.json"))
        self._install_package(package,version)


    def _install_lib_patch(self,package,version,distpath,simulate=False):

        libsdir = env.lib_dir(distpath)
        flds = package.fullname.split(".")
        namespace = flds[1]
        name = flds[2]
        repo = package.repo
        lib_dst = fs.path(libsdir,repo,namespace,name)
        lib_tgt = fs.path(env.lib_dir(env.dist),repo,namespace,name)            
    
        if simulate: return "",lib_tgt

        lib_src = fs.get_tempdir()
        fs.untarxz(package.file,lib_src)
        doc_src = fs.path(lib_src,"docs")
        fs.rmtree(doc_src)
        # clean directories
        fs.rmtree(lib_dst)
        info("    installing in",lib_dst)
        fs.copytree(lib_src,lib_dst)
        fs.del_tempdir(lib_src)
        return lib_dst, lib_tgt

    def _install_sys_patch(self,package,version,distpath):
        sys_src = fs.get_tempdir()
        fs.untarxz(package.file,sys_src)
        pk = fs.get_json(fs.path(sys_src,"package.json"))
        tdir = pk["targetdir"]
        
        if package.fullname.startswith("sys.zerynth.runtime-"):
            # for patches there is no need for newpython hack
            tdir = tdir.replace("newpython","python")
        elif package.fullname.startswith("sys.zerynth.browser-"):
            # remove package.json, not needed as a tool and interfere with nw.js
            fs.rm_file(fs.path(sys_src,"package.json"))
            # no need for newbrowser
            tdir = tdir.replace("newbrowser","browser")
        dst = fs.path(distpath,"sys",tdir)
        info("    installing in",dst)
        fs.copytree(sys_src,dst)
        fs.del_tempdir(sys_src)
        return dst, fs.path(env.sys,tdir)

    def _install_vhal_patch(self,package,version,distpath):
        vhal_src = fs.get_tempdir()
        fs.untarxz(package.file,vhal_src)
        pk = fs.get_json(fs.path(vhal_src,"package.json"))
        tdir = pk["targetdir"]
        dst = fs.path(env.vhal_dir(distpath),tdir)
        info("    installing in",dst)
        fs.copytree(vhal_src,dst)
        fs.del_tempdir(vhal_src)
        return dst, fs.path(env.vhal_dir(env.dist),tdir)

    def _install_device_patch(self,package,version,distpath,simulate=False):
        dev_dst = fs.path(env.devices_dir(distpath),package.fullname.split(".")[2])
        dev_tgt = fs.path(env.devices_dir(env.dist),package.fullname.split(".")[2])
        if simulate: return "",dev_tgt
        fs.rmtree(dev_dst)
        fs.makedirs(dev_dst)
        info("    installing in",dev_dst)
        fs.untarxz(package.file,dev_dst)
        return dev_dst, dev_tgt 


    def _install_core_patch(self,package,version,distpath):
        if package.fullname=="core.zerynth.toolchain":
            dst = env.ztc_dir(distpath)
            pdst = env.ztc_dir(env.dist)
        elif package.fullname=="core.zerynth.studio":
            dst = env.studio_dir(distpath)
            pdst= env.studio_dir(env.dist)
        elif package.fullname=="core.zerynth.stdlib":
            dst = env.stdlib_dir(distpath)
            pdst = env.stdlib_dir(env.dist)
        else:
            # just in case
            dst = fs.path(distpath,package.fullname.split(".")[2])
            pdst= fs.path(env.dist,pacakge.fullname.split(".")[2])
        info("    installing in",dst)
        fs.rmtree(dst)
        fs.untarxz(package.file,dst)
        if package.fullname == "core.zerynth.studio":
            #change package.json for nw.js
            packjson = {
                          "name": "Zerynth Studio",
                          "main": "index.html",
                          "window": {
                            "frame": True,
                            "min_width": 800,
                            "min_height": 600
                          },
                          "version":env.var.version,
                          "user-agent":"ide/%ver/"+env.platform
                        }
            # no icon for mac, it's already in the browser
            if not env.is_mac():
                packjson["window"].update({"icon":"img/Logo512.png"})
            fs.set_json(packjson,fs.path(dst,"package.json"))
        return dst, pdst
    
