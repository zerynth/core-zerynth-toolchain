"""
.. _ztc-cmd-package:

********
Packages
********

The ZTC features a package manager to search, install and publish components of the Zerynth ecosystem.
A package is an archive generated from a tagged git repository and identified by a unique :samp:`fullname`.
There exist several package types, each one targeting a different Zerynth functionality:

* :samp:`core` packages contain core Zerynth components (i.e. the ZTC, the Studio, etc...)
* :samp:`sys` packages contain plaform dependent third party tools used by the ZTC (i.e. gcc, device specific tools, the Python runtime, etc..)
* :samp:`board` packages contain device definitions
* :samp:`vhal` packages contain low level drivers for various microcontroller families
* :samp:`meta` packages contain sets of other packages
* :samp:`lib` packages contain Zerynth libraries to add new modules to Zerynth programs

A package :samp:`fullname` is composed of three fields uniquely identifying the package:

* type
* :ref:`namespace <ztc-cmd-namespace>`
* package name

For example, the package :samp:`lib.broadcom.bmc43362` contains the Python driver for the Broadcom bcm43362 wifi chip. 
Its fullname contains the type (:samp:`lib`), the namespace (:samp:`broadcom`) grouping all packages implementing Broadcom drivers, and the actual package name (:samp:`bcm43362`) specifying which particular driver is implemented.
A package has one or more available versions each one tagged following a modified `semantic versionig <http://semver.org>`_ scheme.

Moreover packages can belong to multiple "repositories" (collections of packages). There are two main public repositories, the :samp:`official` one, containing packages created, published and mantained by the Zerynth team, and the :samp:`community` one, containing packages created by community members.

The ZTC mantains a local databases of installed packages and refers to the online database of packages to check for updates and new packages.

    """
from base import *
import click
import datetime
import json
import sys
import re
import hashlib
import time
import hashlib
from urllib.parse import quote_plus, unquote

_zpm = None

def check_versions():
    try:
        res = zget(url=env.api.repo+"/versions.json", auth=None)
        return res
    except Exception as e:
        warning("Error while checking for updates",e)

def update_versions():
    info("Checking for updates...")
    repopath = fs.path(env.cfg, "versions.json")
    res = check_versions()
    if not res:
        warning("Can't retrieve updates")
    elif res.status_code == 304:
        pass
    elif res.status_code == 200:
        fs.set_json(repopath,res.json(),indent=4)
    else:
        warning("Error checking updates",res.status_code)

@cli.group(help="Manage packages.")
def package():
    global _zpm
    _zpm = Zpm()


@package.command(help="Download online package database")
def sync():
    """
.. _ztc-cmd-package-sync:

Sync
----

The local database of available packages is a copy of the online package database. The command: ::

    ztc package sync

overwrites the local database with the online one. Subsequent ZTC commands on packages will use the updated database.
Most package commands automatically sync package database before executing. Such behaviour can be disabled by providing the :option:`--db` option

    """
    update_versions()


def retrieve_patch_info():
    try:
        res = zget(url=env.patchurl+"/"+env.var.version+"/repository.json",auth=False)
        if res.status_code == 200:
            npth = res.json()
        else:
            debug("No updates available for",env.var.version,[res.status_code])
            return
    except Exception as e:
        warning("Error while asking for updates",env.var.version,e)
        return
    return npth




@package.command(help="Checks and prepares updates")
@click.option("--finalize",flag_value=True,default=False)
def patches(finalize):

    versions = env.versions
    curpatch = env.patches[env.var.version]
    
    if not curpatch:
        warning("Can't retrieve patch info")
        return
   
    patchid = curpatch
    lastpatchid = versions[env.var.version][-1]
    

    if lastpatchid==patchid:
        info("No updates to apply")
        return
   
    pth = retrieve_patch_info()
    if not pth:
        warning("Can't retrieve current patch")
        return

    if finalize and not env.installer_v3:
        fatal("Can't install update! This instance of Zerynth does not support updates: refer to this %link%guide%https://docs.zerynth.com/latest/official/core.zerynth.docs/migration2/docs/index.html%")
 
    # create the patches
    ppath=fs.path(env.tmp,"patch")
    fs.rmtree(ppath)
    fs.makedirs(ppath)
    to_update = []
    pres = {"packs":[]}
    for pack in npth["packs"]:
        fullname = pack["fullname"]
        patches = pack["patches"]
        # retrieve valid patches
        packpatches = [ (x,pack["hashes"][i]) for i,x in enumerate(patches) if x>patchid and x<=lastpatchid ]
        if not packpatches:
            #this package must be skipped, already installed or newer 
            pass
        if pack.get("sys",env.platform)!=env.platform:
            # skip, not for this platform
            pass
        to_update.append(pack)
        if not finalize:
            # skip donwload and install if not finalizing
            continue
        #finalize
        pack = Var({
            "fullname":fullname,
            "version":env.var.version,
            "repo":"official",
            "type":fullname.split(".")[0],
            "file":fs.path(env.tmp,fullname+"-"+env.var.version+".tar.xz")
        })
        packpatch,packhash = packpatches[-1]
        todelete = packhash=="-"
        if not todelete:
            # download and unpack
            info("Downloading",fullname)
            if _zpm._download_package(pack,nfo["version"]) is not True:
                fatal("Error while downloading",fullname)

        if pack.type=="lib":
            src,dst =  _zpm._install_lib_patch(pack,pack.version,ppath,simulate = todelete)
        elif pack.type=="core":
            src,dst =  _zpm._install_core_patch(pack,pack.version,ppath)
        elif pack.type=="board":
            src,dst =  _zpm._install_device_patch(pack,pack.version,ppath,simulate = todelete)
        elif pack.type=="vhal":
            src,dst =  _zpm._install_vhal_patch(pack,pack.version,ppath)
        elif pack.type=="sys":
            src,dst =  _zpm._install_sys_patch(pack,pack.version,ppath)
        else:
            warning("unpatchable package",pack.fullname)
            continue
        pres["packs"].append({
            "destdir":dst,
            "srcdir":src  #src is empty if package need to be deleted
        })
        

    pres["patch"]=npth
    pres["version"]=env.var.version
    if finalize:
        fs.set_json(pres,fs.path(env.tmp,"patchfile.json"))
        # fs.set_json(npth,patchfile)
        info("Update ready!")
    else:
        npth["packs"]=to_update
        log_json(npth)

    

