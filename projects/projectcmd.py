from base import *
import click
import datetime
import json
import sys
import pygit2

proj_url = "http://localhost/zbackend/projects/"

def create_project_entity(path):
    if fs.file_exists(fs.path(path,".zproject")):
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        if "uid" in proj_contents:
            return True
        else:
            headers = {"Authorization": "Bearer "+env.token}
            try:
                res = zpost(url=proj_url, headers=headers, data=proj_contents)
                if res.json()["status"] == "success":
                    proj_contents.update({"uid": res.json()["data"]["uid"]})
                    fs.set_json(proj_contents,fs.path(path,".zproject"))
                    return proj_contents
                else:
                    return False
            except Exception as e:
                return False
    else:
        return None

@cli.group()
def project():
    pass

@project.command()
@click.argument("title")
@click.argument("path",type=click.Path())
@click.option("--description",default="[Project description goes here]")
def create(title,path,description):
    pinfo = {
        "title":title,
        "created_at":str(datetime.datetime.utcnow()),
        "description":description
        }
    fs.makedirs(path)
    if fs.file_exists(fs.path(path,".zproject")):
        error("Can't create project in this folder")
    else:
        info("Creating",fs.path(path,"main.py"))
        fs.write_file("# "+title+"\n# Created at "+pinfo["created_at"]+"\n\n",fs.path(path,"main.py"))
        info("Creating",fs.path(path,"readme.md"))
        fs.write_file(title+"\n"+("="*len(title))+"\n\n"+description,fs.path(path,"readme.md"))
        headers = {"Authorization": "Bearer "+env.token}
        try:
            res = zpost(url=proj_url, headers=headers, data=pinfo)
            if res.json()["status"] == "success":
                pinfo.update({"uid": res.json()["data"]["uid"]})
                info("Project",title,"created with uid:", res.json()["data"]["uid"])
            else:
                warning("Can't create remote project")
        except Exception as e:
            warning("Can't create remote project")
        fs.set_json(pinfo,fs.path(path,".zproject"))

@project.command()
@click.argument("path",type=click.Path())
def create_remote(path):
    res = create_project_entity(path)
    if res is True:
        error("project already in zerynth server")
    elif res is False:
        warning("Can't create remote project")
    elif res is None:
        error("no project in this path")
    else:
        info("Project",res["title"],"created with uid:", res["uid"])

@project.command()
@click.argument("path",type=click.Path())
def delete(path):
    if fs.file_exists(fs.path(path,".zproject")):
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        try:
            fs.rmtree(path, env.is_windows())
            info("deleting project", proj_contents["title"])
            if "uid" in proj_contents:
                try:
                    headers = {"Authorization": "Bearer "+env.token}
                    res = zdelete(url=proj_url+proj_contents["uid"], headers=headers)
                    if res.json()["status"] == "success":
                        info("Project",proj_contents["title"],"deleted from zerynth server")
                    else:
                        warning("Can't delete remote project")
                except Exception as e:
                    warning("Can't delete remote project")
        except Exception as e:
            error("Can't delete the project")
    else:
        error("no project in this path")

@project.command()
@click.argument("path",type=click.Path())
def git_init(path):
    res = create_project_entity(path)
    if res is False:
        critical("Can't create remote project")
    elif res is None:
        error("no project in this path")
    else:
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        info("Project",proj_contents["title"]," with uid:", proj_contents["uid"])
        try:
            headers = {"Authorization": "Bearer "+env.token}
            res = zpost(url=proj_url+proj_contents["uid"]+"/git", headers=headers, data={})
            if res.json()["status"] == "success":
                proj_contents.update({"git_url": res.json()["data"]["git_url"]})
                fs.set_json(proj_contents,fs.path(path,".zproject"))
                info("Project",proj_contents["title"]," linked to git url:", proj_contents["git_url"])    
            elif res.json()["code"] == 400:
                warning("git repository already exists")
            else:
                error("Can't create git remote repository")
                return
            zgit = proj_contents["git_url"]
            zgit = zgit.replace("local://",env.git_url)
            try:
                repo_path = pygit2.discover_repository(path)
                print(repo_path)
                repo = pygit2.Repository(repo_path)
                repo.create_remote("zerynth", "http://"+env.token+":x-oauth-basic@"+zgit)
            except KeyError:
                pygit2.init_repository(path)
                repo_path = pygit2.discover_repository(path)
                print(repo_path)
                repo = pygit2.Repository(path)
                repo.create_remote("zerynth", "http://"+env.token+":x-oauth-basic@"+zgit)
        except Exception as e:
            warning("Can't create git repository", e)


@project.command("import") 
def prj_import():
    pass


@project.command()
def clone():
    pass

@project.command()
def make_doc():
    pass