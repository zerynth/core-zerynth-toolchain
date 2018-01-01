from base import *
import sqlite3
import json
import tarfile
import zlib
import lzma
import time

def download_package(fullname,version,patch="base",hash=None,callback=None):
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

def download_url(url,outfile):
    for attempt in range(6,20,6):
        try:
            r = zgetraw(url)
            with open(outfile,"wb") as f:
                fs.copyfileobj(r,f)
            return True
        except Exception as e:
            debug("download exception",str(e))
        debug("Attempt",str(attempt))
        time.sleep(attempt)
    return False


def install_lib_patch(package,version,distpath,simulate=False):
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

def install_sys_patch(package,version,distpath):
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

def install_vhal_patch(package,version,distpath):
    vhal_src = fs.get_tempdir()
    fs.untarxz(package.file,vhal_src)
    pk = fs.get_json(fs.path(vhal_src,"package.json"))
    tdir = pk["targetdir"]
    dst = fs.path(env.vhal_dir(distpath),tdir)
    info("    installing in",dst)
    fs.copytree(vhal_src,dst)
    fs.del_tempdir(vhal_src)
    return dst, fs.path(env.vhal_dir(env.dist),tdir)

def install_device_patch(package,version,distpath,simulate=False):
    dev_dst = fs.path(env.devices_dir(distpath),package.fullname.split(".")[2])
    dev_tgt = fs.path(env.devices_dir(env.dist),package.fullname.split(".")[2])
    if simulate: return "",dev_tgt
    fs.rmtree(dev_dst)
    fs.makedirs(dev_dst)
    info("    installing in",dev_dst)
    fs.untarxz(package.file,dev_dst)
    return dev_dst, dev_tgt 


def install_core_patch(package,version,distpath):
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

