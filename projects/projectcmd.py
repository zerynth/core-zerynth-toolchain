"""
.. module:: Projects

********
Projects
********

A Zerynth Project is a folder with all the source files and other supported extra file needed to the project itself.
Every Project can be created anywhere on users pc (according to the runner users permissions) and will include a :file:`.zproject` json file with all the main related informations.

Project Commands
================

This module contains all Zerynth Toolchain Commands for managing Zerynth Project Entities.
With this commands the Zerynth Users can handle all their projects using the command-line interface terminal.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Projects are:

* create__: to create a Zerynth Project
* create_remote_: to create a Remote Project Entity in Zerynth Backend
* delete_: to delete a Zerynth Project
* git_init_: to initialize the project folder as a git repository stored in Zerynth Backend
* make_doc_: to generate a documentation related to the project
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

@cli.group(help="Manage Zerynth Projects. This module contains all Zerynth Toolchain Commands for managing Zerynth Project Entities.")
def project():
    pass

@project.command(help="Create a new Zerynth Project. \n\n Arguments: \n\n TITLE: title of the z-project. \n\n PATH: path of the z-project.")
@click.argument("title")
@click.argument("path",type=click.Path())
@click.option("--from","_from",default=False,help="Source to clone another project.")
@click.option("--description",default="[Project description goes here]",help="Description of the project.")
def create(title,path,_from,description):
    """ 
__ create_proj_

.. _create_proj:

Create a Project
----------------

This command is used to create a new Zerynth Project from the command line with this syntax: ::

    Syntax:   ./ztc project create title path --from --description
    Example:  ./ztc project create myProj ~/my/Proj/Folder --description "My First Zerynth Project"

This command take as input the following arguments:
    * **title** (str) --> the title that the users want to give to their project (**required**)
    * **path** (str) --> the valid path where the users want to create the project (**required**)
    * **from** (str) --> the source of another project to clone it (**optional**; default=False)
    * **description** (str) --> the description that the users want to give to their project (**optional**; default=“[Project description goes here]")

**Errors**:
    * Missing input data
    * Passing path with an other existing zerynth project

.. note:: By default the command also creates a remote project entity in the Zerynth Backend to prepare the project for future git operations
.. warning:: If the "Remote Project" creation fails, the users can work on their project only locally but they cannot initialize it as a git repository stored in the Zerynth Backend

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

@project.command(help="Create a new Zerynth Remote Project.\n\n Arguments: \n\n PATH: path of the z-project.")
@click.argument("path",type=click.Path())
def create_remote(path):
    """ 
.. _create_remote:

Create a Remote Project
-----------------------

This command is used to create a new Zerynth Remote Project from the command line running: ::

    Syntax:   ./ztc project create_remote path
    Example:  ./ztc project create_remote ~/my/Proj/Folder

A Remote Project is a Database Entity linked to the related User Local Project stored in the Zerynth Backend.
The creation of this entity permits to the users to prepare the project for future initialization of this folder as a git repository stored in the Zerynth Backend.

This command take as input the following argument:
    * **path** (str) --> the valid path where the users have the project that want to associate to a remote entity (**required**) 

**Errors:**
    * Missing input data
    * Passing path without a zproject inside
    * Passing path with a zproject already existing in the Zerynth Backend
    * Receiving Zerynth Backend response errors
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

@project.command(help="Delete a Zerynth Project.\n\n Arguments: \n\n PATH: path of the z-project.")
@click.argument("path",type=click.Path())
def delete(path):
    """ 
.. _delete:

Delete a Project
----------------

This command is used to delete an existing Zerynth Project from local and from the Zerynth Backend.
The command line for this operation has the following syntax: ::

    Syntax:   ./ztc project delete path
    Example:  ./ztc project delete ~/my/Proj/Folder

This command take as input the following argument:
    * **path** (str) --> the valid path where the users have the zproject that want to remove (**required**) 

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

@project.command(help="Inizialize a Git Repository.\n\n Arguments: \n\n PATH: path of the z-project.")
@click.argument("path",type=click.Path())
def git_init(path):
    """
.. _git_init:

Initialize a Git Repository
---------------------------

This command is used to initialize a zerynth project folder as a git repository hosted in the Zerynth Backend.
This command can be executed by running: ::

    Syntax:   ./ztc project git_init path
    Example:  ./ztc project git_init ~/my/Proj/Folder

This command take as input the following argument:
    * **path** (str) --> the valid path where the users have the zproject that want to initialize as git repository (**required**) 

**Errors:**
    * Missing input data
    * Passing path without a zproject inside
    * Passing a path with a zproject already initialized as a git repository in the Zerynth Backend
    * Receiving Errors from the Zerynth Backend
    
.. note:: 
    After completing this operation, the project folder became a git repository and every git operations can be executed on it in standard way.
    If the users want to push/pull to/from the Zerynth Backend they must execute the git operation with the Zerynth Remote Master. ::
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

@project.command(help="Compile a documentation.\n\n Arguments: \n\n PATH: path of the z-project.")
@click.argument("path",type=click.Path())
def make_doc(path):
    """ 
.. _make_doc:

Compile a Documentation
-----------------------

This command is used to generate an html documentation related to an existing zerynth project.
The command line for this operation has the following syntax: ::

    Syntax:   ./ztc project make_doc path
    Example:  ./ztc project make_doc ~/my/Proj/Folder

This command take as input the following argument:
    * **path** (str) --> the path where the users have the zproject that want to document (**required**) 

**Errors:**
    * Missing input data
    * Passing path without a zproject inside

.. note:: Before running this command, it's recommended to create a “docs" folder inside the related project folder containing a :file:`docs.json` file and a :file:`index.rst` file.\n
          In the :file:`docs.json`, the users must include a json dictionary like below: ::
            
            {
                "title":"Title of your documentation",
                "copyright":"Author of your documentation",
                "version":"Version of your documentation",
                "files":[
                    ["title for file1","source .py or .json for document1"],
                    ["title for file2","source .py or .json for document2"],
                    ["...", "..."]
                ]
            }

          In the :file:`index.rst` file, the users must include the title of the index, the contents (optional) of the index, and the :file:`__toc.rst` file
          automatically generated during docs compilation for producing the complete document index. ::

            ***********
            Index_Title
            ***********

            .. index contents (optional)

            .. include:: __toc.rst

.. warning:: If the "docs" folder, :file:`docs.json` file, and :file:`index.rst` don't exist, the system
             will generate them with default settings that can be edited manually     
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


