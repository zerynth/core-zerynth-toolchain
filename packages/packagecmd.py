"""
.. module:: Packages

********
Packages
********
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
    info("hash for",repo,crc)
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
        if res.status_code == 304:
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

@cli.group()
def package():
    global _zpm
    _zpm = Zpm()


@package.command()
def sync():
    update_repos()

@package.command()
@click.option("--from","_from",default=0)
def published(_from):
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

@package.command()
@click.option("--extended","extended",flag_value=True, default=False,help="output full package info")
def installed(extended):
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

@package.command()
@click.option("--db", flag_value=False, default=True)
def updated(db):
    if db: update_repos()
    installed_list = _zpm.get_installed_list()
    pkgs = {p.fullname:v for p,v in _zpm.get_all_packages() if p.fullname in installed_list and installed_list[p.fullname]!=v}
    if env.human:
        table = [[k,pkgs[k]] for k in sorted(pkgs)]
        log_table(table,headers=["fullaname","version"])
    else:
        log_json(pkgs,cls=ZpmEncoder)



@package.command()
@click.argument("query")
@click.option("--types", default="lib",help="comma separated list of package types: lib, sys, board, vhal, core, meta")
def search(query,types):
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


@package.command()
@click.argument("path",type=click.Path())
@click.argument("version")
@click.option("--git", default=False)
@click.option("--username", default=False)
@click.option("--password", default=False)
def publish(path, version, git,username,password):
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
    pack_contents = {k:v for k,v in pack_contents.items() if k in (needed_fields | valid_fields)}

    # check git url
    if git:
        pack_contents["git_pointer"] = git
    elif fs.exists(fs.path(path,".zproject")):
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        if "git_url" in proj_contents:
            pack_contents["git_pointer"] = proj_contents["git_url"]
            info("Creating package from project", proj_contents["title"])
        else:
            fatal("project must be a git repository")
    else:
        fatal("no project in this folder")
    
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
    ## TODO: UNCOMMENT and add support for meta packages
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

@package.command()
@click.option("-p", multiple=True, type=str)
@click.option("--db", flag_value=False, default=True)
@click.option("--last", flag_value=True, default=False)
@click.option("--force", flag_value=True, default=False)
@click.option("--simulate", flag_value=True, default=False)
@click.option("--justnew", flag_value=True, default=False)
@click.option("--offline", default=False)
@click.option("--mute", flag_value=True, default=False)
def install(p, db, last, force, simulate,justnew,offline,mute):
    
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
            fatal("Error during install",ze)
        except Exception as e:
            critical("Impossible to install packages:", exc=e)


# def update_all(self):
#     installed_list = self.get_installed_list()
#     self.install(packages=installed_list, last=True, force=None,justnew=True)


@package.command()
@click.option("--db", flag_value=False, default=True)
@click.option("--simulate", flag_value=True, default=False)
def update_all(db,simulate):
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
        fatal("Impossible to install packages:", e)

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


@package.command("info")
@click.argument("fullname")
def __info(fullname):
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


