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
import sqlite3
import re
import hashlib
import time
import hashlib
from urllib.parse import quote_plus, unquote
from .zpm  import *
from .zversions import *

_zpm = None

def check_db(repo):
    try:
        crc = fs.file_hash(fs.path(env.edb,repo, "packages.db"))
    except Exception as e:
        #warning(e)
        crc = 0
    headers = {"If-None-Match": str(crc)}
    try:
        res = zget(url=env.api.db+"/"+repo, headers=headers,auth="conditional")
        return res
    except Exception as e:
        warning("Error while asking for db",repo,e)

def update_zdb(repolist):
    has_official = True
    for repo in repolist:
        info("Updating repository ["+repo+"]")
        repopath = fs.path(env.edb, repo)
        info("Checking repository",repo)
        res = check_db(repo)
        if not res:
            warning("Can't update repository",repo)
            continue
        elif res.status_code == 304:
            info(repo, "repository is in sync")
        elif res.status_code == 200:
            info(repo, "repository downloaded")
            fs.makedirs(repopath) 
            fs.write_file(res.content, fs.path(repopath, "repo.tar.xz"))
        else:
            if repo=="official": has_official=False
            warning("Error while downloading repo",repo, res.status_code)
            continue
        #### integrate edb in zdb
        fs.untarxz(fs.path(repopath,"repo.tar.xz"),repopath)

    if has_official:
        _zpm.clear_zpack_db()
        for repo in repolist:
            repopath = fs.path(env.edb, repo, "packages.db")
            if not fs.exists(repopath):
                continue
            tmpdb = sqlite3.connect(repopath)
            for row in tmpdb.execute("select * from packages"):
                res = _zpm.pack_from_row(row)
                _zpm.put_pack(res)
            tmpdb.close()
        _zpm.save_zpack_db()
    else:
        warning("Can't download official repository, sync aborted")

def update_repos():
    # official must be last one, since put_pack replaces existing db entries
    repolist = env.load_repo_list()+["community","official"]
    update_zdb(repolist)

@cli.group(help="Manage packages.")
def package():
    global _zpm
    _zpm = Zpm()




@package.command("info", help="Display package info. \n\n Arguments: \n\n FULLNAME: package fullname.")
@click.argument("fullname")
def __info(fullname):
    """
.. _ztc-cmd-package-info: 
    
Package Info
------------

The command: ::

    ztc package info fullname

displays information about the package identified by :samp:`fullname`.
            
    """
    pack = _zpm.get_pack(fullname)
    if not pack:
        if env.human:
            fatal("No such package:",fullname)
        else:
            log_json({})
            return
    if env.human:
        table = [
            ["fullname",pack.fullname],
            ["last version",pack.last_version],
            ["versions",pack.versions],
            ["title",pack.title],
            ["description",pack.description],
        ]
        log_table(table)
    else:

        log_json(pack.to_dict(),cls=ZpmEncoder)


@package.command(help="Install/update packages.")
@click.option("-p", multiple=True, type=str,help="fullname:version of the package (multi-value option)")
@click.option("--db", flag_value=False, default=True,help="do not sync with online package database")
@click.option("--last", flag_value=True, default=False,help="select most up to date packages")
@click.option("--force", flag_value=True, default=False,help="force installation in case of dependencies errors")
@click.option("--simulate", flag_value=True, default=False,help="print list of required packages without installing them")
@click.option("--justnew", flag_value=True, default=False, help="do not reinstall already installed packages")
@click.option("--offline", default=False, help="path to the directory holding offline packages")
@click.option("--mute", flag_value=True, default=False,help="suppress stdout")
def install(p, db, last, force, simulate,justnew,offline,mute):
    """
.. _ztc-cmd-package-install:

Install
-------

Packages can be added to the current Zerynth installation with the command: ::

    ztc package install -p fullname:version

where :samp:`fullname` is the package fullname and :samp:`version` is the version of the package to install (or update if a previous version is already installed).
The command first downloads the online package database and then recursively check package dependencies in order to install all required packages.

The command accepts many additional options:

* :option:`-p fullname:version` can be repeated multiple times to install more than one package at a time
* :option:`--db` skips the downloading of the online package database
* :option:`--last` while checking dependencies, selects the more up to date version of the dependency
* :option:`--force` performs installation of packages ignoring dependencies errors (warning: this could break the ZTC, use with caution)
* :option:`--justnew` while checking dependencies, avoids installing packages whose version is already installed
* :option:`--simulate` performs a simulated install, printing the list of modified packages only
* :option:`--offline path` performs installation searching packages in :samp:`path` instead of downloading them. Used for offline installations.
* :option:`--mute` supresses messages to stdout


.. note:: when the package :samp:`meta.zerynth.core` is installed, a new ZTC version is created and will be automatically used on subsequent executions of the ZTC. Previously installed versions of the ZTC can be reactivated by modifying the :file:`config.json` setting the :samp:`version` field to the desired value. 

.. note:: packages :samp:`sys.zerynth.runtime` and :samp:`sys.zerynt.browser` are not automatically installed! They are downloaded and uncompressed under :file:`sys/newpython` and :file:`sys/newbrowser` directories respectively. For the packages to be activated, such directories must be renamed to :file:`sys/python` and :file:`sys/browser` respectively.

    """
    
    if mute: set_output_filter(False)
    #### update local db
    if db:
        update_repos()

    #### check packages and its dependecies
    packages = {}
    for pack in p:
        if ':' in pack:
            fullname = pack.split(':')[0]
            version = pack.split(':')[1]
        else:
            fullname = pack
            version = False
        packages.update({fullname: version})

    
    if packages:
        try:
            if offline:
                opkg = fs.get_json(fs.path(offline,"package.json"))
                to_download = {k:v for k,v in opkg["packages"].items()}
                to_download[opkg["name"]]=opkg["version"]
            else:
                to_download = _zpm.generate_installation(packages,last,force,justnew)
            
            if mute: set_output_filter(True)
            if simulate:
                if env.human:
                    table = [[k,to_download[k]] for k in sorted(to_download)]
                    log_table(table,headers=["fullname","version"])
                else:
                    log_json(to_download)
            else:
                res =_zpm.install(to_download,offline=offline)#,download_callback)
                if res:
                    info("New Zerynth version is",res)
                info("Done")
        except ZpmException as ze:
            critical("Error during install",exc=ze)
        except Exception as e:
            critical("Impossible to install packages:", exc=e)


# def update_all(self):
#     installed_list = self.get_installed_list()
#     self.install(packages=installed_list, last=True, force=None,justnew=True)

@package.command(help="Search packages. \n\n Arguments: \n\n QUERY: text query (enclosed in double quotes)")
@click.argument("query")
@click.option("--types", default="lib",help="Comma separated list of package types: lib, sys, board, vhal, core, meta.")
def search(query,types):
    """
.. _ztc-cmd-package-search:

Search
------

To search the online package database issue the command: ::

    ztc package search query

where :samp:`query` is a string composed of terms separated by spaces and optionally by logical operators. Allowed operators are :samp:`&&` for AND and :samp:`||` for OR. Round parentesis can also used.

The terms provided in the :samp:`query` are searched in the following attributes of a package:

* title
* description
* fullname
* list of package keywords

The command accepts the option :option:`--types typelist` where :samp:`typelist` is a comma separated list of package types to be searched. By default, the search is performed on :samp:`lib` packages only and only the first 50 results ordered by relevance are returned.


    """
    ####TODO validate 
    q = query
    query_url = quote_plus(query)
    try:
        prms = {"textquery":q,"types":types}
        res = zget(url=env.api.search, params=prms)
        rj = res.json()
        if rj["status"] == "success":
            if env.human:
                table = []
                for v in rj["data"]:
                    table.append([v["fullname"],v["versions"],v["repo"],v["title"],v["description"],v["num_of_downloads"],v["rating"]])
                log_table(table,headers=["fullname","versions","repository","title","description","downloads","rating"])
            else:
                log_json(rj["data"],sort_keys=True)
        else:
            error("Can't search package",res.json()["message"])
    except Exception as e:
        critical("Can't search package", exc=e)


# A project can be published. The publishing process transforms a project into a Zerynth :samp:`lib` package and makes it available for download in the :samp:`community` repository.

# In order to publish a project some requirements must be met:

# * the project must be remotely saved on the Zerynth backend. Check command :ref:`git_init <ztc-cmd-project-git_init>` for more info.
# * at least a namespace must be owned by the publishing user


@package.command(help="Publish a package. \n\n Arguments: \n\n PATH: project path. \n\n VERSION: version to be published.")
@click.argument("path",type=click.Path())
@click.argument("version")
def publish(path, version):
    """
.. _ztc-cmd-package-publish:

Publishing a package
--------------------

Zerynth projects can be published as library packages and publicly shared on different repositories (default is :samp:`community`). In order to convert a project into a publishable packages some requirements must be met:

* The project must exist as a repository on the Zerynth backend (see :ref:`git_init <ztc-cmd-project-git_init>`)
* The user must own at least a :ref:`namespace <ztc-cmd-namespace-create`
* The project folder must contain a :file:`package.json` file with all relevant package information

In particular, the :file:`package.json` must contain the following mandatory fields:

* :samp:`title`: the title of the package
* :samp:`description`: a longer description of the package
* :samp:`keywords`: an array of keywords that will be used by the package search engine
* :samp:`repo`: the name of the repository to publish to. Users can generally publish only to "community" unless permission is granted for a different repository
* :samp:`fullname`: the unique name of the package obtained from its type (generally :samp:`lib`), a namespace owned or accessible by the user and the actual library name.
* :samp:`whatsnew`: a string describing what has changed from the previous version of the package
* :samp:`dependencies`: a dictionary containing the required packages that must be installed together with the package. A dictionary key is the fullnames of a required package whereas the value is the minimum required version of such package.

An example of :file:`package.json`: ::

    {
        "fullname": "lib.foo.ds1307",
        "title": "DS1307 Real Time Clock",
        "description": "Foo's DS1307 RTC Driver ... ",
        "keywords": [
            "rtc",
            "maxim",
            "time"
        ],
        "repo": "community",
        "whatsnew": "Fixed I2C bugs",
        "dependencies": {
            "core.zerynth.stdlib":"r2.0.0"
        }
        
    }

The previous file describes the package :samp:`lib.foo.ds1307`, published in the :samp:`community` repository under the namespace :samp:`foo`. It is a package for DS1307 RTC that requires the Zerynth standard library to be installed with a version greater or equal then :samp:`r2.0.0`.

The command: ::

    ztc package publish path version

first checks for the validity of the :file:`package.json` at :samp:`path`, then modifies it adding the specified :samp:`version` and the remote git repository url. A git commit of the project is created and tagged with the :samp:`version` parameter; the commit is pushed to the Zerynth backend together with the just created tag. The backend is informed of the new package version and queues it for review. After the review process is finished, the package version will be available for installation.

Package Documentation
^^^^^^^^^^^^^^^^^^^^^

Each published package can feature its own documentation that will be built and hosted on the Zerynth documentation website. The documentation files must be saved under a :file:`docs` folder in the project and formatted as reported :ref:`here <ztc-cmd-project-make_doc>`. It is strongly suggested to build the documentation locally and double check for typos or reStructuredText errors.


Package Examples
^^^^^^^^^^^^^^^^

Packages be distributed with a set of examples stored under an :file:`examples` folder in the project. Each example must be contained in its own folder respecting the following requirements:

* The example folder name will be converted into the example "title" (shown in the Zerynth Studio example panel) by replacing underscores ("_") with spaces
* The example folder can contain any number of files, but only two are mandatory: :file:`main.py`, the entry point file and :file:`project.md`, a description of the example. Both files will be automatically included in the package documentation.

Moreover, for the examples to be displayed in the Zerynth Studio example panel, a file :file:`order.txt` must be placed in the :file:`examples` folder. It contains information about the example positioning in the example tree: ::

    ; order.txt of the lib.adafruit.neopixel package
    ; comments starts with ";"
    ; inner tree nodes labels start with a number of "#" corresponding to their level
    ; leaves corresponds to the actual example folder name
    #Adafruit
        ##Neopixel
           Neopixel_LED_Strips
           Neopixel_Advanced

    ; this files is translated to:
    ; example root
    ; |
    ; |--- ...
    ; |--- ...
    ; |--- Adafruit
    ; |        |--- ...
    ; |        \--- Neopixel
    ; |                |--- Neopixel LED Strips
    ; |                \--- Neopixel Advanced
    ; |--- ...
    ; |--- ...

    """
    info("Checking...")
    projfile = fs.path(path,".zproject")
    packfile = fs.path(path,"package.json")
    if fs.exists(packfile):
        try:
            pack_contents = fs.get_json(packfile)
        except:
            fatal("bad json in package.json")
    else:
        fatal("missing package.json")

    needed_fields = set(["title","description","fullname","keywords","whatsnew","dependencies","repo"])
    valid_fields = set(["exclude","dont-pack","sys","examples","platform","targetdir","tool","git_pointer","sha1","info"])
    given_fields = set(pack_contents.keys())
    if not (needed_fields <= given_fields):
        fatal("missing some needed fields in package.json:",needed_fields-given_fields)
    pack_contents = {k:v for k,v in pack_contents.items() if k in (needed_fields | valid_fields) or k=="git_url"}

    # check git url
    if "git_pointer" in pack_contents:
        # git_pointer is already in packge.json
        pass
    elif fs.exists(projfile):
        # git_pointer not in package.json
        # try taking it from .zproject
        proj_contents = fs.get_json(projfile)
        if "git_url" in proj_contents:
            pack_contents["git_pointer"] = proj_contents["git_url"]
            info("Creating package from project", proj_contents["title"])
        else:
            fatal("Project must be saved remotely! Create git repository first...")
    else:
        fatal("Project must be saved remotely! Create git repository first...")
    
    # start publishing
    info("Preparing git repository...")
    pack_contents["version"]=version
    if not pack_contents.get("git_pointer","").startswith("zerynth://"):
        fs.set_json(pack_contents,packfile)

    ### updating .zproject
    if fs.exists(projfile):
        proj_contents = fs.get_json(projfile)
        proj_contents["git_url"] = pack_contents["git_pointer"]
        proj_contents["package"] = {
            "fullname":pack_contents["fullname"],
            "version":pack_contents["version"],
            "repo":pack_contents["repo"]
        }
        fs.set_json(proj_contents,projfile)


    # manage git repository for project
    if not pack_contents["git_pointer"].startswith("zerynth://"):
        try:
            repo = git.get_repo(path)
            status = git.git_status(path,"zerynth")
            if version not in status["tags"]:
                git.git_commit(path,"Version "+version)
                tag = git.git_tag(path,version)
                git.git_push(path,"zerynth")
                git.git_push(path,"zerynth",tag)
        except Exception as e:
            fatal("Failed attempt at publishing:",e)


    info("Queuing library for review...")
    ### create remotely
    try:
        res = zpost(url=env.api.packages, data=pack_contents)
        rj = res.json()
        if rj["status"] == "success":
            uid = rj["data"]["uid"]
            info("Package",pack_contents["fullname"],"created with uid:", uid)
            #pack_contents.update({"uid": uid})
        else:
            fatal("Can't create package", rj["message"])
    except Exception as e:
        fatal("Can't create package", e)

    ### prepare data to load the new version
    details = {
        "dependencies": pack_contents["dependencies"],
        "whatsnew": pack_contents["whatsnew"]
    }
    try:
        res = zpost(url=env.api.packages+"/"+pack_contents["fullname"]+"/"+version, data=details)
        rj = res.json()
        if rj["status"] == "success":
            info("version",version,"of package",pack_contents["fullname"],"queued for review")
        else:
            error("Can't publish:",rj["message"])
    except Exception as e:
        fatal("Can't publish:", e)

    info("Ok")

#TODO: improve
def download_callback(cursize,prevsize,totsize):
    curperc = int(cursize/totsize*100)
    prevperc = int(prevsize/totsize*100)
    if curperc//10 > prevperc//10:
        log("\b"*20,curperc,"%",sep="",end="")
    if cursize==totsize:
        log("\b"*20,"100%")




@package.command(help="Update all installed packages.")
@click.option("--db", flag_value=False, default=True, help="do not sync with online package database")
@click.option("--simulate", flag_value=True, default=False,help="print list of required packages without installing them")
def update_all(db,simulate):
    """
.. _ztc-cmd-packages-update_all:

Update all packages
-------------------

The current ZTC installation can be updated with the following command: ::

    ztc package update_all

All packages are checked for new versions and installed. If the :samp:`meta.zerynth.core` packages is updated, a new ZTC installation is also created.

Options :option:`--db` and :option:`--simulate` are available with the same meaning as in the :ref:`install <ztc-cmd-package-install>` command.
    """
    if db:
        update_repos()
    try:
        installed_list = _zpm.get_installed_list()
        to_download = _zpm.generate_installation(installed_list,last=True,force=False,justnew=True)
        if simulate:
            if env.human:
                table = [[k,to_download[k]] for k in sorted(to_download)]
                log_table(table,headers=["fullname","version"])
            else:
                log_json(to_download)
        else:
            res =_zpm.install(to_download)#,download_callback)
            if res:
                info("New Zerynth version is",res)
    except Exception as e:
        critical("Impossible to install packages:", exc=e)

# #TODO: check uninstall
# @package.command()
# @click.option("-p", multiple=True, type=str)
# def uninstall(p):
#     packages = []
#     for pack in p:
#         packages.append(pack)
#     try:
#         _zpm.uninstall(packages)
#     except Exception as e:
#         fatal("impossible to unistall packages:", e)


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
    update_repos()

@package.command(help="List all user published packages.")
@click.option("--from","_from",default=0,help="skip the first n published packages")
def published(_from):
    """
.. ztc-cmd-package-published:

Published packages
------------------

The command: ::

    ztc package published

retrieves the list of packages published by the user.

    """
    try:
        prms = {"from":_from}
        res = zget(url=env.api.packages,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            log_json(rj["data"])
        else:
            error("Can't get published packages",rj["message"])
    except Exception as e:
        critical("Can't get published packages",exc=e)

@package.command(help="List of all installed Zerynth Packages.")
@click.option("--extended","extended",flag_value=True, default=False,help="Flag for output full package info.")
def installed(extended):
    """
.. _ztc-cmd-package-installed:

Installed packages
------------------

The list of currently installed packages can be retrieved with: ::

    ztc package installed

providing the :option:`--extended` prints additional information.

    """
    table = []
    headers = []
    if not extended:
        installed_list = _zpm.get_installed_list()
        for k in sorted(installed_list):
            table.append([k,installed_list[k]])
        headers = ["fullname","version"]
    else:
        installed_list = [v.to_dict() for v in _zpm.get_all_installed_packages()]
        for v in installed_list:
            table.append([v["fullname"],v["last_version"],v["repo"],v["title"],v["rating"]])
        headers = ["fullname","last version","repository","title","rating"]
    if env.human:
        log_table(table,headers=headers)
    else:
        log_json(installed_list,cls=ZpmEncoder)

@package.command(help="List all updatable packages.")
@click.option("--db", flag_value=False, default=True,help="do not sync with online package database")
def updated(db):
    """
.. ztc-cmd_package-updated:

Updated packages
----------------

The list of packages with updated versions with respect to the current installation can be retrieved with: ::
    
    ztc package updated

    """
    if db: update_repos()
    installed_list = _zpm.get_installed_list()
    pkgs = {}
    for p,v in _zpm.get_all_packages():
        if p.fullname in installed_list:
            iv = ZpmVersion(installed_list[p.fullname])
            cv = ZpmVersion(v)
            if cv>iv:
                pkgs[p.fullname]=v
    #pkgs = {p.fullname:v for p,v in _zpm.get_all_packages() if p.fullname in installed_list and ZpmVersion(installed_list[p.fullname])>ZpmVersion(v)}
    table=[]
    if env.human:
        table = [[k,pkgs[k]] for k in sorted(pkgs)]
        log_table(table,headers=["fullname","version"])
    else:
        log_json(pkgs,cls=ZpmEncoder)


@package.command(help="List all available packages.")
@click.option("--db", flag_value=False, default=True,help="do not sync with online package database")
def available(db):
    """
.. ztc-cmd_package-available:

Available packages
------------------

The list of packages available on the backend can be retrieved with: ::
    
    ztc package available

    """
    if db: update_repos()
    pkgs = {p.fullname:v for p,v in _zpm.get_all_packages()}
    table=[]
    if env.human:
        table = [[k,pkgs[k]] for k in sorted(pkgs)]
        log_table(table,headers=["fullname","version"])
    else:
        log_json(pkgs,cls=ZpmEncoder)


@package.command(help="List all updatable packages.")
@click.option("--db", flag_value=False, default=True,help="do not sync with online package database")
def devices(db):
    """
.. ztc-cmd_package-devices:

New Devices
-----------

The list of new supported devices with respect to the current installation can be retrieved with: ::
    
    ztc package devices

    """
    if db: update_repos()
    installed_list = _zpm.get_installed_list()
    pkgs = {}
    for p,v in _zpm.get_all_packages():
        if p.fullname not in installed_list and p.type=="board":
            pkgs[p.fullname]=v
    if env.human:
        table = [[k,pkgs[k]] for k in sorted(pkgs)]
        log_table(table,headers=["fullname","version"])
    else:
        log_json(pkgs,cls=ZpmEncoder)

def md5(file_or_data):
    hh = hashlib.new("md5")
    if isinstance(file_or_data,str):
        hh.update(fs.readfile(file_or_data,"r"))
    else:
        hh.update(file_or_data)
    return hh.hexdigest()

def retrieve_patch_info(base=False):
    try:
        if base:
            fname = "patchbase-"+env.platform+".json"
        else:
            fname = "patch-"+env.platform+".json"

        res = zget(url=env.patchurl+"/patches/"+env.var.version+"/"+fname,auth=False)
        if res.status_code == 200:
            npth = res.json()
        else:
            warning("No patches available for",env.var.version,[res.status_code])
            return
    except Exception as e:
        warning("Error while asking for patches",env.var.version,e)
        return
    return npth



@package.command(help="Checks and prepares patches")
@click.option("--finalize",flag_value=True,default=False)
def patches(finalize):
    patchdir = fs.path(env.dist)
    patchfile = fs.path(patchdir,"patches.json")
    if not fs.exists(patchfile):
        npth = retrieve_patch_info(True)
        if not npth:
            return
        fs.set_json(npth,patchfile)

    pth={}
    crc=""
    if fs.exists(patchfile):
        pth = fs.get_json(patchfile)
        pid = pth.get("patchid","")
    if pth.get("version",env.var.version)!=env.var.version:
        warning("wrong version in patch file",pth["version"],"vs",env.var.version)
        return
    npth = retrieve_patch_info()
    if not npth:
        return   
    new_pid = npth["patchid"]
    if new_pid==pid:
        info("No patches to apply")
        return
    if "ignore" in npth:
        # save to file but ignore
        fs.set_json(npth,patchfile)
        info("No patches to apply")
        return

    info("Patch",npth["patchid"],"available")
    # create the patches
    ppath=fs.path(env.tmp,"patch")
    fs.rmtree(ppath)
    fs.makedirs(ppath)
    pres = {"packs":[]}
    toskip = set()
    for fullname,nfo in npth["packs"].items():
        ohash = pth["packs"][fullname]["hash"] if fullname in pth["packs"] else ""
        chash = nfo["hash"]
        if ohash==chash:
            info("Skipping",fullname,": no changes")
            toskip.add(fullname)
            continue
        if not finalize:
            # skip donwload and install if not finalizing
            continue
        pack = Var({
            "fullname":fullname,
            "version":nfo["version"],
            "repo":"official",
            "type":fullname.split(".")[0],
            "file":fs.path(env.tmp,fullname+"-"+nfo["version"]+".tar.xz")
        })
        # download and unpack
        info("Downloading",fullname)
        if _zpm._download_package(pack,nfo["version"]) is not True:
            fatal("Error while downloading",fullname)
        
        if pack.type=="lib":
            src,dst =  _zpm._install_lib_patch(pack,pack.version,ppath)
        elif pack.type=="core":
            src,dst =  _zpm._install_core_patch(pack,vers,ppath)
        elif pack.type=="board":
            src,dst =  _zpm._install_device_patch(pack,vers,ppath)
        elif pack.type=="vhal":
            src,dst =  _zpm._install_vhal_patch(pack,vers,ppath)
        elif pack.type=="sys":
            src,dst =  _zpm._install_sys_patch(pack,vers,ppath)
        else:
            warning("unpatchable package",pack.fullname)
            continue
        pres["packs"].append({
            "destdir":dst,
            "srcdir":src
        })
    pres["patch"]=npth
    if finalize:
        fs.set_json(pres,fs.path(env.tmp,"patchfile.json"))
        fs.set_json(npth,patchfile)
        info("Patches ready!")
    else:
        for ts in toskip:
            npth["packs"].pop(ts)
        log_json(npth)


    

