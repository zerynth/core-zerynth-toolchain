from base import *
import click
import datetime
import json
import sys
import pygit2
import sqlite3

pack_url = "http://localhost/zbackend/packages/"
db_url = "http://localhost/zbackend/database/"

def check_db(repo):
    headers = {"Authorization": "Bearer "+env.token}
    crc = fs.untarxz(fs.path(repo,"repo.tar.xz"),fs.path(repo, "packages.db"), crc_enable=True)
    headers.update({"If-None-Match": str(crc)})
    try:
        repo = repo.split("/")[-1]
        res = zget(url=db_url+repo, headers=headers)
        return res
    except Exception as e:
        fatal("Server is Down", e)

def update_zdb(repo):
    fs.untarxz(fs.path(repo,"repo.tar.xz"),fs.path(repo, "packages.db"))
    tmpdb = sqlite3.connect(fs.path(repo, "packages.db"))
    for row in tmpdb.execute("select * from packages"):
        res = {
            "uid":row[0],
            "fullname":row[1],
            "type":row[2],
            "tag":row[3],
            "authname":row[4],
            "last_version":row[5],
            "dependencies":row[6], 
            "whatsnew":row[7],
            "rating":row[8],
            "num_of_votes":row[9],
            "num_of_downloads":row[10],
            "last_update":row[11]
            }
        env.put_pack(res)
    fs.rm_file(fs.path(repo, "packages.db"))

@cli.group()
def package():
    pass

@package.command()
@click.argument("path",type=click.Path())
@click.argument("version")
@click.option("--git", default=False)
def publish(path, version, git):
    ####TODO check here if version is in correct ZpmVersion format??
    ###ctrl package.json
    if fs.file_exists(fs.path(path,"package.json")):
        try:
            pack_contents = fs.get_json(fs.path(path,"package.json"))
        except TypeError:
            fatal("invalid json file")
    else:
        fatal("missing package.json file in this folder")
    ###check if is a project or not --> TODO ctrl user permissions in token
    if git:
        if "git_url" in pack_contents:
            git_pointer = pack_contents["git_pointer"]
            info("Creating package from gitlab")
        else:
            fatal("missing git url in package.json")
    elif fs.file_exists(fs.path(path,".zproject")):
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        if "git_url" in proj_contents:
            git_pointer = proj_contents["git_url"]
            info("Creating package from project", proj_contents["title"])
        else:
            fatal("project must be a git repository")
    else:
        fatal("no project in ths folder")
    ###start package pubblication
    headers = {"Authorization": "Bearer "+env.token}
    pack_contents.update({"version": version, "git_pointer": git_pointer})
    try:
        res = zpost(url=pack_url, headers=headers, data=pack_contents)
        #print(res.json())
        if res.json()["status"] == "success":
            uid = res.json()["data"]["uid"]
            last_version = res.json()["data"]["last_version"]
            info("Package",pack_contents["name"],"updated in database with uid:", uid)
            pack_contents.update({"uid": uid, "last_version": last_version})
        else:
            fatal("Can't create package", res.json()["message"])
    except Exception as e:
        fatal("Can't create package", e)
    try:
        #####TODO check signature configuration of pygit2
        repo_path = pygit2.discover_repository(path)
        repo = pygit2.Repository(repo_path)
        index = repo.index
        index.add_all()
        tree = repo.index.write_tree()
        commit = repo.create_commit("HEAD", repo.default_signature, repo.default_signature, "version: "+version, tree, [repo.head.target])
        #print(commit)
        cc = repo.revparse_single("HEAD")
        repo.remotes["zerynth"].push(['refs/heads/master'])
        try:
            tag = repo.create_tag(version, cc.hex, pygit2.GIT_OBJ_COMMIT, cc.author, cc.message)
            #print(tag)
            repo.remotes["zerynth"].push(['refs/tags/'+version])
            info("Updated repository with new version:",version,"for the package", pack_contents["name"])
        except Exception as e:
            fatal("Can't create package", e)
    except KeyError:
        fatal("no git repositories in this path")
    ###prepare data for load the new version in server database
    details = {
        "details":{
            "version": version,
            "dependencies": pack_contents["dependencies"],
            "whatsnew": pack_contents["whatsnew"]
        }
    }
    try:
        res = zpost(url=pack_url+pack_contents["uid"]+"/"+version, headers=headers, data=details)
        if res.json()["status"] == "success":
            info("new version:",version,"loaded into server database, in waiting to be approved")
        else:
            error("Can't create package",res.json()["message"])
    except Exception as e:
        error("Can't create package", e)
    

@package.command()
@click.argument("fullname")
@click.argument("version")
@click.option("--db", flag_value=True, default=False)
def install(fullname, version, db):
    
    #### update local dbs
    for repo in fs.dirs(env.edb):
        res = check_db(repo)
        if res.status_code == 304:
            info(repo, "database already at server version")
        elif res.status_code == 200:
            info(repo, "uploading new last server version...")
            fs.write_bytes_file(res.content, fs.path(env.edb, repo, "repo.tar.xz"))
        else:
            error(repo, "--> Error from the server", res.status_code)
            continue
        #### integrate edb in zdb
        res = update_zdb(repo)



    
    

    #### check package and its dependecies
    