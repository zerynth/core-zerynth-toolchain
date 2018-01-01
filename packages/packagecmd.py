"""
.. _ztc-cmd-package:

********
Packages
********

The ZTC features a package manager to search and install components of the Zerynth ecosystem.
A package is an archive generated from a tagged git repository and identified by a unique :samp:`fullname`.
There exist several package types, each one targeting a different Zerynth functionality:

* :samp:`core` packages contain core Zerynth components (i.e. the ZTC, the Studio, etc...)
* :samp:`sys` packages contain plaform dependent third party tools used by the ZTC (i.e. gcc, device specific tools, the Python runtime, etc..)
* :samp:`board` packages contain device definitions
* :samp:`vhal` packages contain low level drivers for various microcontroller families
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
import webbrowser
from urllib.parse import quote_plus, unquote
from .zpm import *

def check_versions():
    try:
        res = zget(url=env.api.repo+"/versions", auth=None)
        return res
    except Exception as e:
        warning("Error while checking for updates",e)

def update_versions():
    repopath = fs.path(env.cfg, "versions.json")
    res = check_versions()
    if not res:
        warning("Can't retrieve updates")
    elif res.status_code == 304:
        pass
    elif res.status_code == 200:
        fs.set_json(res.json(),repopath)
        return res.json()
    else:
        warning("Error checking updates",res.status_code)

@cli.group(help="Manage packages.")
def package():
    pass


@package.command(help="Retrieve and store current distributions")
def versions():
    """
.. _ztc-cmd-package-sync:

Versions
--------

The available versions of Zerynth can be retrieved with the command: ::

    ztc package versions

The command overwrites the local copy of available versions.

    """
    try:
        vrs = update_versions()
        if vrs:
            if not env.human:
                res = {
                    "versions":{},
                    "latest":env.var.version,
                    "last_patch": env.patches[env.var.version],
                    "major_update":False,
                    "minor_update":False
                }
                for v,p in vrs.items():
                    res["versions"][v]=p
                    if compare_versions(v,env.var.version)>0:
                        if compare_versions(res["latest"],v)<0:
                            res["latest"]=v
                            res["last_patch"]=p[-1]
                            res["major_update"]=True
                if not res["major_update"]:
                    res["last_patch"]=res["versions"][env.var.version][-1]
                    res["minor_update"] = env.patches[env.var.version]!=res["last_patch"]

                log_json(res)
            else:
                table = []
                for v,p in vrs.items():
                    table.append([v,p])
                log_table(table,headers=["version","patches"])
    except Exception as e:
        fatal("Can't check versions",e)



@package.command("info",help="Get info for package")
@click.argument("fullname")
def get_info(fullname):
    npth = retrieve_community()
    if not npth: 
        fatal("Can't find package info")

    for p in npth:
        if p["fullname"]==fullname:
            log_json(p)
            break
    else:
        fatal("Can't find package",fullname)


@package.command(help="Retrieve and store current available packages")
@click.argument("version")
def available(version):
    """
.. _ztc-cmd-package-available:

Available packages
------------------

The list of official packages for a specific version of Zerynth can be retrieved with the command: ::

    ztc package available version

The command returns info on every official Zerynth package.

    """
    try:
        nfo = retrieve_packages_info()
        if nfo:
            if not env.human:
                log_json(nfo)
            else:
                table = []

                for pack in nfo["packs"]:
                    table.append([pack["fullname"],pack["patches"],pack["size"]//1024])
                table.sort()
                log_table(table,headers=["fullname","patches","size Kb"])
    except Exception as e:
        fatal("Can't check packages",e)

@package.command(help="Describe a patch relative to current installation")
@click.argument("patch")
def describe(patch):
    """
.. _ztc-cmd-package-describe:

Describe patch
--------------

The difference between the current installation of Zerynth and a new patch can be described with the command: ::

    ztc package describe patch


    """
    try:
        curpatch = env.patches[env.var.version]
        if patch<=curpatch:
            return
        nfo = retrieve_packages_info()
        if nfo:
            res = {
                "packs":[],
                "changelog":""
            }
            pos = nfo["patches"].index(patch)
            if pos:
                res["changelog"]=nfo["changelog"][pos]
            for pack in nfo["packs"]:
                fullname = pack["fullname"]
                patches = pack["patches"]
                # retrieve valid patches
                packpatches = [ (x,pack["hashes"][i]) for i,x in enumerate(patches) if x>curpatch and x<=patch ]
                if not packpatches:
                    #this package must be skipped, already installed or newer 
                    continue
                if pack.get("sys",env.platform)!=env.platform:
                    # skip, not for this platform
                    continue
                res["packs"].append({
                    "fullname":fullname,
                    "size":pack["size"],
                    "hash":pack["hashes"][patches.index(packpatches[-1])]
                })

            if not env.human:
                log_json(res)
            else:
                table = []

                for pack in res:
                    table.append([pack["fullname"],pack["hash"],pack["size"]//1024])
                table.sort()
                log_table(table,headers=["fullname","hash","size Kb"])
    except Exception as e:
        fatal("Can't describe patch",e)

@package.command(help="Triggers a major Zerynth update")
def trigger_update():
    """
.. _ztc-cmd-package-trigger:

Trigger Update
--------------

As soon as a new major release of Zerynth is available, it can be installed by triggering it with the following command: ::

    ztc package trigger_install

The next time the Zerynth installer is started, it will try to install the new version of Zerynth. 
    """
    fs.set_json({"version":env.var.version},fs.path(env.tmp,"major_release.json"))




@package.command(help="Install community packages")
@click.argument("fullname")
@click.argument("version")
def install(fullname,version):
    """
.. _ztc-cmd-package-install:

Install community packages
--------------------------

Community packages can be installed and updated with the following command: ::

    ztc package install fullname version

The package archive will be downloaded and installed from the corresponding Github release tarball.
    
    """
    flds = fullname.split(".")
    user = flds[1]
    reponame = flds[2]
    if flds[0]!="lib":
        fatal("No such package",fullname)
    # github url
    tarball = "https://github.com/"+user+"/"+reponame+"/archive/"+version+".tar.gz"
    outfile = fs.path(env.tmp,"community-"+user+"-"+reponame+".tar.gz")
    #namespace
    destdir = fs.path(env.libs,"community",user.replace("-","_"))
    #temporary unpacked dir
    tdir = fs.path(destdir,reponame+"-"+version)
    #reponame dir
    edir = fs.path(destdir,reponame.replace("-","_"))
    #ztc file with info
    zfile = fs.path(edir,".zerynth")
    try:
        info("Downloading",tarball) 
        if download_url(tarball,outfile):
            #untar
            fs.rmtree(tdir)
            fs.rmtree(edir)
            fs.makedirs(destdir)
            info("Unpacking in",destdir)
            fs.untargz(outfile,destdir)
            #rename dir to correct reponame
            fs.move(tdir,edir)
            fs.set_json({
                "fullname":fullname,
                "version":version,
                "url":"https://github.com/"+user+"/"+reponame+"/tree/"+version,
                "import":user.replace("-","_")+"."+reponame.replace("-","_")
                },zfile)
            retrieve_community()
            info("Done")
        else:
            warning("Can't download",fullname)
    except Exception as e:
        warning("Can't install",fullname,e)
        fs.rmtree(tdir)
        fs.rmtree(edir)



@package.command(help="Authorize Zerynth to access Github use info")
def authorize():
    try:
        res = zget(url=env.api.profile)
        rj = res.json()
        if rj["status"]=="success":
            state = rj["data"]["github"]["challenge"]
        else:
            fatal("Can't retrieve user info")
        log("Hello!")
        log("In a few seconds a browser will open to the login page")
        log("Once logged, copy the authorization token and paste it here")
        time.sleep(1)
        webbrowser.open(env.api.github+"?client_id=99fdc1e39d8ce3051ce6&scope=user&state=-"+state)
        token = input("Paste the token here and press enter -->")
        user,token = token.split(":")
        fs.set_json({"user":user,"access_token":token},fs.path(env.cfg,"github.json"))
        info("Done")
    except Exception as e:
        fatal("Can't get Github authorization",e)

@package.command(help="Publish a community library")
@click.argument("repo")
@click.argument("nfofile")
def publish(repo,nfofile):
    nfo = fs.get_json(nfofile)
    if not nfo.get("keywords") or not nfo.get("title") or not nfo.get("description"):
        fatal("Missing fields in",nfofile)

    data = {
        "repo":repo,
        "title":nfo["title"],
        "description":nfo["description"],
        "keywords":nfo["keywords"]
    }
    try:
        res = zpost(env.api.community,data)
        log(res)
        log(res.content)
        rj = res.json()
        if rj["status"] == "success":
            info("Thanks for publishing! You will shortly receive an email with the library status")
        else:
            fatal("Can't publish!",rj["message"])
    except Exception as e:
        fatal("Can't publish",e)

    

def retrieve_packages_info(version=None):
    if not version:
        version = env.var.version
    try:
        res = zget(url=env.api.repo+"/repository/"+version,auth=False)
        if res.status_code == 200:
            npth = res.json()
            return npth
        else:
            debug("Can't get package list for",version,[res.status_code])
    except Exception as e:
        warning("Can't get package list for",version,e)

@package.command(help="Get community repository")
@click.option("--force",default=False,flag_value=True)
def repository(force):
    npth = retrieve_community(force)
    if npth:
        log_json(npth)

def retrieve_community(force=False):
    try:
        pfile = fs.path(env.cfg,"community.json")
        retrieve = not fs.exists(pfile) or fs.unchanged_since(pfile,3600) or force 
        if retrieve:
            debug("Retrieve from network")
            res = zget(url=env.api.repo+"/community",auth=False)
            if res.status_code == 200:
                npth = res.json()
                fs.set_json(npth,fs.path(env.cfg,"community.json"))
            else:
                debug("Can't get community repo",[res.status_code])
                if fs.exists(pfile):
                    npth = fs.get_json(pfile)
                else:
                    npth={}
        else:
            debug("Retrieve from disk")
            npth = fs.get_json(pfile)
        fln = {p["fullname"]:p for p in retrieve_installed_community()}
        for pp in npth:
            pp["last_version"]=pp["versions"][-1]
            fp = fln.get(pp["fullname"])
            if fp:
                pp["installed"]=fp["version"]
        
        return npth
    except Exception as e:
        warning("Can't get community repo",e)


def retrieve_installed_community():
    community = fs.all_files(fs.path(env.libs,"community"),filter=".zerynth")
    for p in community:
        try:
            pp = fs.get_json(p)
            yield {
                "fullname":pp["fullname"],
                "version":pp["version"],
                "url":pp["url"]
            }
        except:
            # .zerynth missing or bad
            pass


@package.command(help="List of all installed packages")
def installed():
    """
.. _ztc-cmd-package-installed:

Installed packages
------------------

The list of currently installed official and community packages (of type lib) can be retrieved with: ::

    ztc package installed

    """
    table = []
    inst = []
    official = fs.all_files(fs.path(env.libs,"official"),filter="package.json")
    for p in official:
        try:
            pp = fs.get_json(p)
            inst.append({
                "fullname":pp["fullname"],
                "last_version":env.var.version,
                "repo":"official",
                "installed":env.var.version,
                "title":pp["title"],
                "keywords":pp.get("keywords",[]),
                "description":pp["description"]
                })
            table.append([pp["fullname"],env.var.version,"official",pp["title"],0])
        except:
            # subdirs can contain spurious package.json files
            pass
    for pp in retrieve_installed_community():
        inst.append({
            "fullname":pp["fullname"],
            "last_version":pp["version"],
            "repo":"community",
            "url":pp["url"]
        })

    if env.human:
        log_table(table,headers=["fullname","last version","repository","title","rating"])
    else:
        log_json(inst)




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
            if download_package(pack,nfo["version"]) is not True:
                fatal("Error while downloading",fullname)

        if pack.type=="lib":
            src,dst =  install_lib_patch(pack,pack.version,ppath,simulate = todelete)
        elif pack.type=="core":
            src,dst =  install_core_patch(pack,pack.version,ppath)
        elif pack.type=="board":
            src,dst =  install_device_patch(pack,pack.version,ppath,simulate = todelete)
        elif pack.type=="vhal":
            src,dst =  install_vhal_patch(pack,pack.version,ppath)
        elif pack.type=="sys":
            src,dst =  install_sys_patch(pack,pack.version,ppath)
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

    

