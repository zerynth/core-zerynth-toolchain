"""
.. module:: Packages

********
Packages
********

The Zerynth Package is extra plug-in of the Zerynth Backend composed by a file or a group of files 
encasing several specific tested features that customers can add to their projects installing it on their pc.

Each z-package is published in a domain related to a namespace directly linked to owner user in order to 
permit that every package has an unique and unambiguous path.

There are several types of Zerynth Packages; here a brief description:

* **core**: principal z-packages on which are based all the Zerynth Tools (Zerynth Studio, Zerynth Toolchain, Standard Library)
* **sys**: z-packages to add system tool platform dependent (Windows, Linux, Mac)
* **board**: z-packages to add new devices to the Zerynth Tools
* **vhal**: z-packages for virtual hardware abstract layer to add low level drivers grouped for microcontroller families
* **lib**: z-packages to add specific class and features to improve new features the z-devices
* **meta**: z-packages that contains list of other z-packages to be installed

Package Commands
================

This module contains all Zerynth Toolchain Commands for interacting with Zerynth Package Entities.
With this commands the Zerynth Users can install new available packages in their installation or can publish a new one 
using the command-line interface terminal.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Packages are:

* info_: to display a Zerynth Package informations
* install_: to install one or more Zerynth Packages
* search__: to search Zerynth Packages according to keywords passed as text query
* publish_: to publisha new Zerynth Package
* update_all_: to update to the last version all Zerynth Packages already installed
* sync_: to sync all z-user local repository database
* published_: to display the list of published z-packages 
* installed_: to display the list of installed z-packages
* updated_: to display the list of updated z-packages
    """
from base import *
import click
import datetime
import json
import sys
import pygit2
import sqlite3
import re
import hashlib
import time
from urllib.parse import quote_plus, unquote
from .zpm  import *
from .zversions import *

_zpm = None

def check_db(repo):
    try:
        crc = fs.file_hash(fs.path(env.edb,repo, "packages.db"))
    except Exception as e:
        warning(e)
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

@cli.group(help="Manage Zerynth Package. This module contains all Zerynth Toolchain Commands for managing Zerynth Package Entities.")
def package():
    global _zpm
    _zpm = Zpm()



@package.command("info", help="Display Zerynth Package information. \n\n Arguments: \n\n FULLNAME: fullname of the z-package.")
@click.argument("fullname")
def __info(fullname):
    """
.. _info: 
    
Display Package Info
--------------------


This command is used to display informations for specific Zerynth Package passed as argument from the command line running: ::

    Syntax:   ./ztc package info fullname
    Example:  ./ztc package info pack_type.namespace.pack_name

This command take as input the following argument:
    * **fullname** (str) --> the fullname of the z-package (**required**) 

**Errors**:
    * Missing required data
    * Receiving Zerynth Backend response errors

.. note::   The fullname of a z-package is composed by the package type, the package namespace and the package name separated by a dot.
            
    """
    pack = _zpm.get_pack(fullname)
    if not pack:
        fatal("No such package:",fullname)
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


@package.command(help="Install a Zerynth Package.")
@click.option("-p", multiple=True, type=str,help="Array of packages (fullname:version) to be installed (multi-value option).")
@click.option("--db", flag_value=False, default=True,help="Flag for not updating local z-package database.")
@click.option("--last", flag_value=True, default=False,help="Flag for installing z-package last version.")
@click.option("--force", flag_value=True, default=False,help="Flag for forcing installation of z-packages.")
@click.option("--simulate", flag_value=True, default=False,help="Flag for simulatin z-package installation.")
@click.option("--justnew", flag_value=True, default=False, help="Flag for installing only new z-packages.")
@click.option("--offline", default=False, help="The path of the package for the offline installation.")
@click.option("--mute", flag_value=True, default=False,help="Flag for no diplay log message output.")
def install(p, db, last, force, simulate,justnew,offline,mute):
    """
.. _install:

Install a Package
-----------------

This command is used to install one or more Zerynth Packages on proper installation from the command line running: ::

    Syntax:   ./ztc package install -p --db --last --force --simulate --justnew --offline --mute
    Example:  ./ztc package install -p pack1_type.namespace1.pack1_name -p pack2_type.namespace2.pack_name2 

This command take as input the following arguments:
    * **p** (array) --> list of packages in format fullname:version to be installed (**optional**, default=[]) 
    * **db** (bool) --> flag for not updating local z-package database (**optional**, default=True)
    * **last** (bool) --> flag for installing z-package last version (**optional**, default=False) 
    * **force** (bool) --> flag for forcing installation of z-packages (**optional**, default=False) 
    * **simulate** (bool) --> flag for simulating package installation and display the Zerynth Package Manager operation results (**optional**, default=False) 
    * **justnew** (bool) --> flag for installing only new z-packages against the already installed packages (**optional**, default=False) 
    * **offline** (str) --> the path of the package for the offline installation (**optional**, default=False) 
    * **mute** (bool) --> flag for no diplay log message output (**optional**, default=False) 

**Errors**:
    * Missing required data
    * Conflicts in Package Dependencies
    * Zerynth Package Manager error messages
    * Receiving Zerynth Backend response errors

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

@package.command(help="Search Zerynth Packages by query. \n\n Arguments: \n\n QUERY: text query for searching in the Zerynth Database.")
@click.argument("query")
@click.option("--types", default="lib",help="Comma separated list of package types: lib, sys, board, vhal, core, meta.")
def search(query,types):
    """
__ search_pack_

.. _search_pack:

Search Packages
---------------

This command is used to search Zerynth Packages on Zerynth Database from the command line with the following syntax: ::

    Syntax:   ./ztc package search query --types
    Example:  ./ztc package search "key1 && (key2 || key3)" --types "lib,board"  

This command take as input the following arguments:
    * **query** (str) --> text query allowing logic operations between keyword (**required**) 
    * **types** (str) --> Comma separated list of package types: lib, sys, board, vhal, core, meta (**optional**, default=“lib")
    
**Errors**:
    * Missing required data
    * Receiving Zerynth Backend response errors

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


@package.command(help="Publish a new Zerynth Package. \n\n Arguments: \n\n PATH: Path to the z-project to be published. \n\n VERSION: version of the published package.")
@click.argument("path",type=click.Path())
@click.argument("version")
@click.option("--git", default=False)
def publish(path, version, git):
    """
.. _publish:

Publish a Package
-----------------

This command is used to publish a owned Zerynth Project transforming it in a new Zerynth Package.
Before publish a z-packages, the Zerynth Users must create their onw namespace to assiciate the related z-package.
The Zerynth Users can publish only "library" type z-packages running from the command line: ::

    Syntax:   ./ztc package publish path version
    Example:  ./ztc package publish ~/my/proj/folder "r1.0.0"  

This command take as input the following arguments:
    * **path** (str) --> path of the z-project to be published (**required**) 
    * **version** (str) --> version of the published package (**required**)
    
**Errors**:
    * Missing required data
    * Missing package.json file with related required fields
    * Missing z-project or git repository associated
    * Receiving Zerynth Backend response errors

.. note:: For publishing a new package is needed a :file:`package.json` file inside
          the passed path argument containing a dictionary with the following required fields: ::
            
            {
                "name":"Z-Package Name",
                "description": "Z-Package Description",
                "fullname": "Z-Package Fullname,
                "keywords":[
                    "key1",
                    "key2",
                    "...",
                ]
                "dependencies":{
                    "dep_pack1": "vers_dep_pack1",
                    "dep_pack2": "vers_dep_pack2",
                    "...": "...",
                },
                "whatsnew":{
                    "description": "What's new description",
                },
                "repo": [
                    "official/community",
                    "...",
                ]
            }

    """
    ####TODO check here if version is in correct ZpmVersion format??
    if fs.exists(fs.path(path,"package.json")):
        try:
            pack_contents = fs.get_json(fs.path(path,"package.json"))
        except:
            fatal("bad json in package.json")
    else:
        fatal("missing package.json")

    needed_fields = set(["title","description","fullname","keywords","whatsnew","dependencies","repo"])
    valid_fields = set(["exclude","dont-pack","sys","examples","platform","targetdir","tool"])
    given_fields = set(pack_contents.keys())
    if not (needed_fields <= given_fields):
        print(needed_fields)
        print(given_fields)
        print(needed_fields<given_fields)
        fatal("missing some needed fields in package.json:",needed_fields-given_fields)
    pack_contents = {k:v for k,v in pack_contents.items() if k in (needed_fields | valid_fields) or k=="git_url"}

    # check git url
    if git:
        if "git_pointer" in pack_contents:
            pass
        else:
            pack_contents["git_pointer"] = git
    elif fs.exists(fs.path(path,".zproject")):
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        if "git_url" in proj_contents:
            pack_contents["git_pointer"] = proj_contents["git_url"]
            info("Creating package from project", proj_contents["title"])
        else:
            fatal("project must be a git repository")
    print(pack_contents)
    # start publishing
    pack_contents["version"]=version
    fs.set_json(pack_contents,fs.path(path,"package.json"))
    
    try:
        res = zpost(url=env.api.packages, data=pack_contents)
        rj = res.json()
        if rj["status"] == "success":
            uid = rj["data"]["uid"]
            info("Package",pack_contents["fullname"],"created with uid:", uid)
            pack_contents.update({"uid": uid})
        else:
            fatal("Can't create package", rj["message"])
    except Exception as e:
        fatal("Can't create package", e)


    # manage git repository for project
    # try:
    #     #####TODO check signature configuration of pygit2
    #     repo_path = pygit2.discover_repository(path)
    #     repo = pygit2.Repository(repo_path)
    #     regex = re.compile('^refs/tags')
    #     tags = filter(lambda r: regex.match(r), repo.listall_references())
    #     tags = [x.replace("refs/tags/","") for x in tags]
    #     if version in tags:
    #         fatal("Version",version,"already present in repo tags",tags)
    #     index = repo.index
    #     index.add_all()
    #     tree = repo.index.write_tree()
    #     commit = repo.create_commit("HEAD", repo.default_signature, repo.default_signature, "version: "+version, tree, [repo.head.target])
    #     #print(commit)
    #     cc = repo.revparse_single("HEAD")
    #     remote = "zerynth" if not git else "origin"
    #     credentials = None if (not username and not password) else pygit2.RemoteCallbacks(pygit2.UserPass(username,password))
    #     repo.remotes[remote].push(['refs/heads/master'],credentials)

    #     try:
    #         tag = repo.create_tag(version, cc.hex, pygit2.GIT_OBJ_COMMIT, cc.author, cc.message)
    #         #print(tag)
    #         repo.remotes[remote].push(['refs/tags/'+version],credentials)
    #         info("Updated repository with new tag:",version,"for", pack_contents["fullname"])
    #     except Exception as e:
    #         critical("Can't create package", exc=e)
    # except KeyError:
    #     fatal("no git repositories in this path")

    ###prepare data to load the new version
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
            error("Can't publish package",rj["message"])
    except Exception as e:
        critical("Can't publish package", exc=e)

#TODO: improve
def download_callback(cursize,prevsize,totsize):
    curperc = int(cursize/totsize*100)
    prevperc = int(prevsize/totsize*100)
    if curperc//10 > prevperc//10:
        log("\b"*20,curperc,"%",sep="",end="")
    if cursize==totsize:
        log("\b"*20,"100%")




@package.command(help="Update all installed z-packages.")
@click.option("--db", flag_value=False, default=True, help="Flag for not updating local z-package database.")
@click.option("--simulate", flag_value=True, default=False,help="Flag for simulating the update of all installed packages.")
def update_all(db,simulate):
    """
.. _update_all:

Update all Packages
-------------------

This command is used to update all the Zerynth Packages installed on the z-user pc from the command line running: ::

    Syntax:   ./ztc package update_all --db --simulate
    Example:  ./ztc package update_all   

This command take as input the following arguments:
    * **db** (bool) -->  flag for not updating local z-package database (**optional**, default=True) 
    * **simulate** (bool) --> flag for simulating the update of all installed packages and display the Zerynth Package Manager operation results (**optional**, default=False)
    
**Errors**:
    * Conflicts in Package Dependencies
    * Zerynth Package Manager error messages
    * Receiving Zerynth Backend response errors

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


@package.command(help="Sync local repo database with the remote one.")
def sync():
    """
.. _sync:

Syncronize all Local Repositories
---------------------------------

This command is used to sync all the Local Repository Database with the Zerynth Remote Repository Database accessible for the related z-user from the command line running: ::

    Syntax:   ./ztc package sync
    Example:  ./ztc package sync   

This command take no argument as input:
    
**Errors**:
    * Receiving Zerynth Backend response errors

.. note:: The Syncronization of local repositories is automatically executed in the "install","update_all" and "updated" commands without the ``--db`` flag.

    """
    update_repos()

@package.command(help="List all published Zerynth Packages.")
@click.option("--from","_from",default=0,help="Number from which list the published z-packages.")
def published(_from):
    """
.. _published:

List of Published Packages
--------------------------

This command is used to list all proper Published Zerynth Packages from the command line running: ::

    Syntax:   ./ztc package published --from
    Example:  ./ztc package published   

This command take as input the following argument:
    * **from** (int) --> number from which list the published z-packages (**optional**, default=0) 
    
**Errors**:
    * Receiving Zerynth Backend response errors

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
.. _installed:

List of Installed Packages
--------------------------

This command is used to list all the already Installed Zerynth Packages from the command line running: ::

    Syntax:   ./ztc package installed --extended
    Example:  ./ztc package installed   

This command take as input the following argument:
    * **extended** (bool) --> flag for output full package info (**optional**, default=False) 

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

@package.command(help="List all Updatable Zerynth Package.")
@click.option("--db", flag_value=False, default=True,help="Flag for not updating local z-package database.")
def updated(db):
    """
.. _updated:

List of Updated Packages
------------------------

This command is used to list all Zerynth Packages that are updated against all those installed on the z-user pc from the command line running: ::

    Syntax:   ./ztc package updated --db
    Example:  ./ztc package updated 

This command take as input the following argument:
    * **db** (bool) -->  flag for not updating local z-package database (**optional**, default=True) 
    
**Errors**:
    * Receiving Zerynth Backend response errors

    """
    if db: update_repos()
    installed_list = _zpm.get_installed_list()
    pkgs = {p.fullname:v for p,v in _zpm.get_all_packages() if p.fullname in installed_list and installed_list[p.fullname]!=v}
    if env.human:
        table = [[k,pkgs[k]] for k in sorted(pkgs)]
        log_table(table,headers=["fullname","version"])
    else:
        log_json(pkgs,cls=ZpmEncoder)


