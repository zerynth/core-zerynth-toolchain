"""
.. module:: Projects

****************
Project Commands
****************
"""

from base import *
import click
import datetime
import json
import sys
import pygit2


def create_project_entity(path):
    if fs.exists(fs.path(path,".zproject")):
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        if "uid" in proj_contents:
            return True
        try:
            res = zpost(url=env.api.project, data=proj_contents)
            rj = res.json()
            if rj["status"] == "success":
                proj_contents.update({"uid": rj["data"]["uid"]})
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
    """
This module contains all Zerynth Toolchain Commands for managing Zerynth Project Entities.
With this commands the Zerynth User can handle all his projects using the command-line interface terminal.

Every Project can be created anywhere on user pc and will include a :file:`.zproject` json
file with all the main related informations.
    """
    pass

@project.command()
@click.argument("title")
@click.argument("path",type=click.Path())
@click.option("--from","_from",default=False,help="source to clone another project")
@click.option("--description",default="[Project description goes here]",help="description of the project")
def create(title,path,_from,description):
    """ 
================
Create a Project
================

This command is used to create a new Zerynth Project from the command line with this syntax: ::

    Syntax:   ./ztc project create title path --from --description
    Example:  ./ztc project create myProj ~/my/Proj/Folder --description "My First Zerynth Project"

This command invokes the :func:`create` function

.. function:: create(title, path, from=False, descritption="[Project description goes here]")

**Args**:
    * **title:** argument containing the title that the user wants to give to his project (type **string** --> **required**)
    * **path:** argument containing where the user wants to create the project (type **string-path** --> **required**)
    * **from:** argument containing the source of another zerynth project to clone it (type **string** --> **optional**)
    * **description:** argument containing the description that the user wants to give to his project (type **string** --> **optional**)

This function returns several log messages to inform the user about the results of the operation. 

This operation cannot succeed for missing input data or project creation in a folder where there is an other existing zerynth project.

.. note:: By default the command also create a remote project entity in the Zerynth Server to prepare the project for future git operations
.. warning:: If the Remote Project creation failed, the user can work on his project only locally but he cannot initialize it as a git repository stored in the Zerynth Server

    """
    pinfo = {
        "title":title,
        "created_at":str(datetime.datetime.utcnow()),
        "description":description
    }
    fs.makedirs(path)
    if fs.exists(fs.path(path,".zproject")):
        error("A project already exists in",path)
    else:
        if _from:
            info("Cloning from",_from)
            fs.copytree(_from,path)
        else:
            info("Writing",fs.path(path,"main.py"))
            fs.write_file("# "+title+"\n# Created at "+pinfo["created_at"]+"\n\n",fs.path(path,"main.py"))
            info("Writing",fs.path(path,"readme.md"))
            fs.write_file(title+"\n"+("="*len(title))+"\n\n"+description,fs.path(path,"readme.md"))
        # REMOTE API CALL
        try:
            res = zpost(url=env.api.project, data=pinfo)
            rj = res.json()
            if rj["status"] == "success":
                pinfo.update({"uid": rj["data"]["uid"]})
                info("Project",title,"created with uid:", rj["data"]["uid"])
            else:
                warning("Can't create remote project")
        except Exception as e:
            warning("Can't create remote project")
            print(e)
        fs.set_json(pinfo,fs.path(path,".zproject"))

@project.command()
@click.argument("path",type=click.Path())
def create_remote(path):
    """ 
=======================
Create a Remote Project
=======================

This command is used to create a new Zerynth Remote Project from the command line with this syntax: ::

    Syntax:   ./ztc project create_remote path
    Example:  ./ztc project create_remote ~/my/Proj/Folder

A Remote Project is a Database Entity linked to the related User Local Project stored in the Zerynth Server.
The creation of this entity permits to the user to prepare the project for future initialization of this folder as a git repository stored in the Zerynth Server.

.. function:: create_remote(path)

**Args**:
    * **path:** argument containing where the user has the project that wants to associate to a remote entity (type **string-path** --> **required**)

This function returns several log messages to inform the user about the results of the operation. 

**Errors:**
    * Missing input data
    * Passing path without a zproject inside
    * Passing path with a zproject already existing in the Zerynth Server
    * Receiving Zerynth Server response errors
    """
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
    """ 
================
Delete a Project
================

This command is used to delete an existing Zerynth Project from local and from the Zerynth Server.
The command line for this operation has the following syntax: ::

    Syntax:   ./ztc project delete path
    Example:  ./ztc project delete ~/my/Proj/Folder

This command invokes the :func:`delete` function

.. function:: delete(path)

**Args**:
    * **path:** argument containing where the user has the zproject that wants to remove (type **string-path** --> **required**)

This function returns several log messages to inform the user about the results of the operation. 

**Errors:**
    * Missing input data
    * Passing path without a zproject inside
    """
    if fs.exists(fs.path(path,".zproject")):
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        try:
            fs.rmtree(path, env.is_windows())
            info("deleting project", proj_contents["title"])
            if "uid" in proj_contents:
                try:
                    res = zdelete(url=env.api.project+proj_contents["uid"])
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
    """ 
===========================
Initialize a Git Repository
===========================

This command is used to initialize a zerynth project folder as a git repository hosted in the Zerynth Server.
The command line for this operation has the following syntax: ::

    Syntax:   ./ztc project git_init path
    Example:  ./ztc project git_init ~/my/Proj/Folder

This command invokes the :func:`git_init` function

.. function:: git_init(path)

**Args**:
    * **path:** argument containing where the user has the zproject that wants to git initialize (type **string-path** --> **required**)

This function returns several log messages to inform the user about the results of the operation. 

**Errors:**
    * Missing input data
    * Passing path without a zproject inside
    * Passing a path with a zproject already initialized as a git repository in the Zerynth Server
    * Receiving Errors from the Zerynth Server
    
.. note:: After completing this operation, the project folder became a git repository and every git operations can be executed on it in standard way.
          If the user wants to push/pull to/from the Zerynth Server he must execute the git operation with the Zerynth Remote Master. ::
              Example:  git push/pull zerynth master
    """
    res = create_project_entity(path)
    if res is False:
        critical("Can't create remote project")
    elif res is None:
        error("no project in this path")
    else:
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        info("Project",proj_contents["title"]," with uid:", proj_contents["uid"])
        try:
            res = zpost(url=env.api.project+proj_contents["uid"]+"/git", data={})
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


# @project.command("import") 
# def prj_import():
#     pass


# @project.command()
# def clone():
#     pass

@project.command()
@click.argument("path",type=click.Path())
def make_doc(path):
    """ 
=======================
Compile a Documentation
=======================

This command is used to generate an html documentation related to an existing zerynth project.
The command line for this operation has the following syntax: ::

    Syntax:   ./ztc project make_doc path
    Example:  ./ztc project make_doc ~/my/Proj/Folder

This command invokes the :func:`make_doc` function

.. function:: make_doc(path)

**Args**:
    * **path:** argument containing where the user has the zproject that wants to document (type **string-path** --> **required**)

This function returns several log messages to inform the user about the results of the operation. 

**Errors:**
    * Missing input data
    * Passing path without a zproject inside
    """
    docpath = fs.path(path,"docs")
    docjson = fs.path(docpath,"docs.json")
    htmlpath = fs.path(fs.get_hashdir("docs"+path),"html")
    print(htmlpath)
    docidx  = fs.path(docpath,"index.rst")
    ##############TO REMOVE these comments
    # if not fs.exists(fs.path(path,".zproject")):
    #     error("No project at",path)
    # proj = fs.get_json(fs.path(path,".zproject"))
    if not fs.exists(docpath) or not fs.exists(docjson) or not fs.exists(docidx):
        # create docs skeleton
        fs.makedirs(docpath)
        files = fs.files(path)
        fs.set_json({
            "version":"",
            "title":proj["title"],
            "files":[ [fs.rpath(fname,path)[0:-3],fs.rpath(fname,path)] for fname in files if fname.endswith(".py") ]
        },docjson)
        fs.write_file(
        "*"*len(proj["title"])+"\n"+
        proj["title"]+"\n"+
        "*"*len(proj["title"])+"\n\n"+
        "\n.. The text you write here will appear in the first doc page. (This is just a comment, will not be rendered)\n\n"+
        ".. include:: __toc.rst\n\n"
        ,docidx)
    #clean html
    fs.rmtree(htmlpath)
    # put conf.py in place
    fs.copyfile(fs.path(fs.dirname(__file__),"conf.py"),fs.path(docpath,"conf.py"))
    # run sphinx
    import sphinx
    code = sphinx.build_main(argv=["sphinx","-b","html",docpath,htmlpath])
    if not code:
        fs.rm_file(fs.path(docpath,"conf.py"))
        fs.rm_file(fs.path(docpath,"layout.html"))
        fs.copyfile(fs.path(fs.dirname(__file__),"zerynth.css"),fs.path(htmlpath,"_static","zerynth.css"))
        info("Docs built")
    else:
        error("Can't build docs!")


