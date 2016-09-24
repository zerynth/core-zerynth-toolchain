from base import *
import click
import datetime

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
    fs.set_json(pinfo,fs.path(path,".zproject"))
    info("Creating",fs.path(path,"main.py"))
    fs.write_file("# "+title+"\n# Created at "+pinfo["created_at"]+"\n\n",fs.path(path,"main.py"))
    info("Creating",fs.path(path,"readme.md"))
    fs.write_file(title+"\n"+("="*len(title))+"\n\n"+description,fs.path(path,"readme.md"))

    #TODO: call zapi

    info("Project",title,"created")


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