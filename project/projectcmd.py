from base import *
import click
import datetime
import requests
import json

headers = {"Content-Type": "application/json"}
proj_url = "http://localhost:7070/projects/"

@cli.group()
def project():
    pass

@project.command()
@click.argument("title")
@click.argument("path",type=click.Path())
@click.option("--description",default="[Project description goes here]")
def create(title,path,description):
    pinfo = {
        "project":{
            "title":title,
            "created_at":str(datetime.datetime.utcnow()),
            "description":description
            }
        }
    fs.makedirs(path)
    if fs.file_exists(path+"/.zproject"):
        error("Can't create project in this folder")
    else:
        info("Creating",fs.path(path,"main.py"))
        fs.write_file("# "+title+"\n# Created at "+pinfo["project"]["created_at"]+"\n\n",fs.path(path,"main.py"))
        info("Creating",fs.path(path,"readme.md"))
        fs.write_file(title+"\n"+("="*len(title))+"\n\n"+description,fs.path(path,"readme.md"))
        
        headers.update({"Authorization": "Bearer "+env.token})
        try:
            res = requests.post(url=proj_url, headers=headers, data=json.dumps(pinfo, cls=base.ZjsonEncoder))
            if res.json()["status"] == "success":
                pinfo["project"].update({"uid": res.json()["data"]["proj_uid"]})
                info("Project",title,"created with uid:", res.json()["data"]["proj_uid"])
            else:
                warning("Can't create remote project")
        except Exception as e:
            warning("Can't create remote project")
        fs.set_json(pinfo,fs.path(path,".zproject"))

@project.command()
@click.argument("path",type=click.Path())
def create_remote(path):
    if fs.file_exists(path+"/.zproject"):
        proj_contents = fs.get_json(path+"/.zproject")
        if "uid" in proj_contents["project"]:
            error("project already in zerynth server")
        else:
            created_at = proj_contents["project"]["created_at"]
            del proj_contents["project"]["created_at"]
            headers.update({"Authorization": "Bearer "+env.token})
            try:
                res = requests.post(url=proj_url, headers=headers, data=json.dumps(proj_contents, cls=base.ZjsonEncoder))
                if res.json()["status"] == "success":
                    proj_contents["project"].update({"uid": res.json()["data"]["proj_uid"], "created_at": created_at})
                    fs.set_json(proj_contents,fs.path(path,".zproject"))
                    info("Project",proj_contents["project"]["title"],"created with uid:", res.json()["data"]["proj_uid"])
                else:
                    warning("Can't create remote project")
            except Exception as e:
                warning("Can't create remote project")
    else:
        error("no project in this path")        

@project.command()
@click.argument("path",type=click.Path())
def delete(path):
    if fs.file_exists(path+"/.zproject"):
        proj_contents = fs.get_json(path+"/.zproject")
        try:
            print(env.is_windows)
            fs.rmtree(path, env.is_windows)
            info("deleting project", proj_contents["project"]["title"])
            if "uid" in proj_contents["project"]:
                try:
                    headers.update({"Authorization": "Bearer "+env.token})
                    res = requests.delete(url=proj_url+proj_contents["project"]["uid"], headers=headers, data=json.dumps(proj_contents, cls=base.ZjsonEncoder))
                    if res.json()["status"] == "success":
                        info("Project",proj_contents["project"]["title"],"deleted from zerynth server")
                    else:
                        warning("Can't delete remote project")
                except Exception as e:
                    warning("Can't delete remote project")
        except Exception as e:
            error("Can't delete the project", e)
    else:
        error("no project in this path")

@project.command()
def publish():
    pass


@project.command("import") 
def prj_import():
    pass


@project.command()
def clone():
    pass

@project.command()
def make_doc():
    pass