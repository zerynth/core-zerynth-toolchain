"""
.. _ztc-cmd-project:

********
Projects
********

A Zerynth project consists of a directory containing source code files, documentation files and other assets as needed.
The project directory must also contain a :file:`.zproject` file containing information about the project. :file:`.zproject` creation and management is completely handled by the ZTC.

The following project commands are available: 

* :ref:`create <ztc-cmd-project-create>`
* :ref:`git_init <ztc-cmd-project-git_init>` and related repository management commands
* :ref:`list <ztc-cmd-project-list>` remote projects
* :ref:`make_doc <ztc-cmd-project-make_doc>`

    """

from base import *
import click
import datetime
import json
import sys
import webbrowser
import re

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

@cli.group(help="Manage projects.")
def project():
    pass

@project.command(help="Create a new project. \n\n Arguments: \n\n TITLE: title of the project. \n\n PATH: path of the project.")
@click.argument("title")
@click.argument("path",type=click.Path())
@click.option("--from","_from",default=False,help="Create a clone of another project from the given path")
@click.option("--description",default="[Project description goes here]",help="Description of the project.")
def create(title,path,_from,description):
    """ 
.. _ztc-cmd-project-create:

Create a project
----------------

A project can be created by issuing the following command: ::

    ztc project create title path

where :samp:`title` is a string (preferably enclosed in double quotes) representing the title of the project and :samp:`path` is the path to the directory that will hold the project files. If such directory does not exist, it is created. If a project already exists at :samp:`path`, the command fails. 

An empty project consists of three files:

* :file:`main.py`, the empty template for the entry point of the program.
* :file:`readme.md`, a description file initially filled with project title and description in markdown format.
* :file:`.zproject`, a project info file used by the ZTC.


Projects can also be stored remotely on the Zerynth backend as git repositories. In order to do so, during project creation, an attempt is made to create a new project entity on the backend and prepare it to receive git operations. If such attempt fails, the project is still usable locally and can be remotely added later.

The :command:`create` can also accept the following options:

* :option:`--from from` where :samp:`from` is a path. If the option is given, all files and directories stored at :samp:`from` will be recursively copied in the new project directory. If the project directory at :samp:`path` already exists, its contents will be deleted before copying from :samp:`from`.
* :option:`--description desc` where :samp:`desc` is a string (preferably enclosed in double quotes) that will be written in :file:`readme.md`

    """
    pinfo = {
        "title":title,
        "created_at":str(datetime.datetime.utcnow()),
        "description":description
    }
    fs.makedirs(path)
    if fs.exists(fs.path(path,".zproject")):
        error("A project already exists at",path)
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
        fs.set_json(pinfo,fs.path(path,".zproject"))

# @project.command(help="Create a new Zerynth Remote Project.\n\n Arguments: \n\n PATH: path of the z-project.")
# @click.argument("path",type=click.Path())
# def create_remote(path):
#     """ 
# .. _create_remote:

# Create a Remote Project
# -----------------------

# This command is used to create a new Zerynth Remote Project from the command line running: ::

#     Syntax:   ./ztc project create_remote path
#     Example:  ./ztc project create_remote ~/my/Proj/Folder

# A Remote Project is a Database Entity linked to the related User Local Project stored in the Zerynth Backend.
# The creation of this entity permits to the users to prepare the project for future initialization of this folder as a git repository stored in the Zerynth Backend.

# This command take as input the following argument:
#     * **path** (str) --> the valid path where the users have the project that want to associate to a remote entity (**required**) 

# **Errors:**
#     * Missing input data
#     * Passing path without a zproject inside
#     * Passing path with a zproject already existing in the Zerynth Backend
#     * Receiving Zerynth Backend response errors
#     """
#     res = create_project_entity(path)
#     if res is True:
#         error("project already in zerynth server")
#     elif res is False:
#         warning("Can't create remote project")
#     elif res is None:
#         error("no project in this path")
#     else:
#         info("Project",res["title"],"created with uid:", res["uid"])

# @project.command(help="Delete a Zerynth Project.\n\n Arguments: \n\n PATH: path of the z-project.")
# @click.argument("path",type=click.Path())
# def delete(path):
#     """ 
# .. _delete:

# Delete a Project
# ----------------

# This command is used to delete an existing Zerynth Project from local and from the Zerynth Backend.
# The command line for this operation has the following syntax: ::

#     Syntax:   ./ztc project delete path
#     Example:  ./ztc project delete ~/my/Proj/Folder

# This command take as input the following argument:
#     * **path** (str) --> the valid path where the users have the zproject that want to remove (**required**) 

# **Errors:**
#     * Missing input data
#     * Passing path without a zproject inside
#     """
#     if fs.exists(fs.path(path,".zproject")):
#         proj_contents = fs.get_json(fs.path(path,".zproject"))
#         try:
#             fs.rmtree(path, env.is_windows())
#             info("deleting project", proj_contents["title"])
#             if "uid" in proj_contents:
#                 try:
#                     res = zdelete(url=env.api.project+proj_contents["uid"])
#                     if res.json()["status"] == "success":
#                         info("Project",proj_contents["title"],"deleted from zerynth server")
#                     else:
#                         warning("Can't delete remote project")
#                 except Exception as e:
#                     warning("Can't delete remote project")
#         except Exception as e:
#             error("Can't delete the project")
#     else:
#         error("no project in this path")


@project.command(help="Initialize a repository.\n\n Arguments: \n\n PATH: project path.")
@click.argument("path",type=click.Path())
def git_init(path):
    """
.. _ztc-cmd-project-git_init:

Initialize a Git Repository
---------------------------

Projects can be stored as private remote git repositories on the Zerynth backend. In order to do so it is necessary to initialize a project as a git repository with the command: ::

    ztc project git_init path

where :samp:`path` is the project directory.

If the project is not already registered in the backend, the remote creation is performed first and a bare remote repository is setup. 
Subsequently, if the project directory already contains a git repository, such repository is configured by adding a new remote called :samp:`zerynth`. Otherwise a fresh git repository is initialized.

Zerynth remote repositories require authentication by basic HTTP authentication mechanism. The HTTPS url of the git repository is modified by adding the user token as username and :samp:`x-oath-basic` as password. If the token expires or is invalidated, the :command:`git_init` command can be repeated to update the remote with a fresh token.

    """
    import pygit2
    res = create_project_entity(path)
    if res is False:
        fatal("Can't create remote project")
    elif res is None:
        fatal("No project at",path)
    else:
        proj_contents = fs.get_json(fs.path(path,".zproject"))
        try:
            res = zpost(url=env.api.project+"/"+proj_contents["uid"]+"/git", data={})
            if res.json()["status"] == "success":
                proj_contents.update({"git_url": res.json()["data"]["git_url"]})
                fs.set_json(proj_contents,fs.path(path,".zproject"))
            elif res.json()["code"] == 400:
                warning("Project repository already exists")
            else:
                fatal("Can't create git remote repository:",res.json()["message"])
            zgit = proj_contents["git_url"]
            zgit = zgit.replace("local://",env.git_url+"/")
            info("Project repository created at",zgit)
            token = get_token(True)
            if not token:
                fatal("Invalid token!")
            authgit = zgit.replace("https://","https://"+token+":x-oauth-basic@")
            try:
                repo = git.get_repo(path,no_fatal=True)
            except:
                git.git_init(path)
                repo = git.get_repo(path,no_fatal=True)
            git.create_remote(path,"zerynth",authgit)
        except Exception as e:
            fatal("Can't create git repository:", e)

@project.command(help="Show repository status.\n\n Arguments: \n\n PATH: project path.")
@click.argument("path",type=click.Path())
@click.option("--remote",default="zerynth",help="select remote, default is zerynth")
def git_status(path,remote):
    """
.. _ztc-cmd-project-git_status:

Check repository status
-----------------------

The command: ::

    ztc project git_status path

Returns information about the current status of the repository at :samp:`path`. In particular the current branch and tag, together with the list of modified files not yet committed. 
It also returns the status of the repository HEAD with respect to the selected remote. The default remote is :samp:`zerynth` and can be changed with the option :option:`--remote`.

    """
    res = git.git_status(path,remote)
    if env.human:
        log("Remote:",remote)
        log("Status:",res["status"])
        log("Branch:",res["branch"])
        log(" Files:",len(res["changes"]))
        for k,v in res["changes"].items():
            log("        "+k)
    else:
        log_json(res)


@project.command(help="Fetch repository.\n\n Arguments: \n\n PATH: project path.")
@click.argument("path",type=click.Path())
@click.option("--remote",default="zerynth",help="select remote, default is zerynth")
def git_fetch(path,remote):
    """
.. _ztc-cmd-project-git_fetch:

Fetch repository
----------------

The command: ::

    ztc project git_fetch path

is equivalent to the :samp:`git fetch` command executed at :samp:`path'. The default remote is :samp:`zerynth` and can be changed with the option :option:`--remote`.

    """
    git.git_fetch(path,remote)
            
@project.command(help="Commit changes.\n\n Arguments: \n\n PATH: project path.")
@click.argument("path",type=click.Path())
@click.option("-m","--msg",default="commit",help="set commit message")
def git_commit(path,msg):
    """
.. _ztc-cmd-project-git_commit:

Commit
------

The command: ::

    ztc project git_commit path -m message

is equivalent to the command sequence :samp:`git add .` and :samp:`git commit -m "message"` executed at :samp:`path`.

    """
    git.git_commit(path,msg)

@project.command(help="Push changes.\n\n Arguments: \n\n PATH: project path.")
@click.argument("path",type=click.Path())
@click.option("--remote",default="zerynth",help="select remote, default is zerynth")
def git_push(path,remote):
    """
.. _ztc-cmd-project-git_push:

Push to remote
--------------

The command: ::

    ztc project git_push path --remote remote

is equivalent to the command :samp:`git push origin remote` executed at :samp:`path`.

    """
    git.git_push(path,remote)

@project.command(help="Pull changes from remote.\n\n Arguments: \n\n PATH: project path.")
@click.argument("path",type=click.Path())
@click.option("--remote",default="zerynth",help="select remote, default is zerynth")
def git_pull(path,remote):
    """
.. _ztc-cmd-project-git_pull:

Pull from remote
----------------

The command: ::

    ztc project git_pull path --remote remote

is equivalent to the command :samp:`git pull` executed at :samp:`path` for remote :samp:`remote`.

    """
    git.git_pull(path,remote)

@project.command(help="Create a new branch or switch to existing branch.\n\n Arguments: \n\n PATH: project path \n BRANCH: branch name.")
@click.argument("path",type=click.Path())
@click.argument("branch")
@click.option("--remote",default="zerynth",help="select remote, default is zerynth")
def git_branch(path,branch,remote):
    """
.. _ztc-cmd-project-git_branch:

Switch/Create branch
--------------------

The command: ::

    ztc project git_branch path branch  --remote remote

behave differently if the :samp:`branch` already exists locally. In this case the command checks out the branch. If :samp:`branch` does not exist, it is created locally and pushed to the :samp:`remote`.

    """
    git.git_branch(path,branch,remote)

@project.command(help="Clone a project repository.\n\n Arguments: \n\n PROJECT: project uid\nPATH: project path")
@click.argument("project")
@click.argument("path",type=click.Path())
def git_clone(project,path):
    """
.. _ztc-cmd-project-git_clone:

Clone a project
---------------

The command: ::

    ztc project git_clone project path

retrieves a project repository saved to the Zerynth backend and clones it to :samp:`path`. The parameter :samp:`project` is the project uid assigned dring project creation. It can be retrieved with the :ref:`list command <ztc-project-list>`.

    """

    git.git_clone(project,path)



@project.command("list", help="List remote projects")
@click.option("--from","_from",default=0,help="skip the first n remote projects")
def __list(_from):
    """
.. _ztc-cmd-project-list:

List remote projects
--------------------

The command: ::

    ztc project list

retrieves the list of projects saved to the Zerynth backend. Each project is identified by an :samp:`uid`.
The max number of results is 50, the option :samp:`--from n` can be used to specify the starting index of the list to be retrieved.

    """
    table=[]
    try:
        prms = {"from":_from}
        res = zget(url=env.api.project,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            if env.human:
                for k in rj["data"]["list"]:
                    table.append([_from,k["uid"],k["title"],k["last_modification"],k["git_pointer"],k["published"]])
                    _from += 1
                log_table(table,headers=["UID","Title","Modified","Git","Published"])
            else:
                log_json(rj["data"])
        else:
            critical("Can't get project list",rj["message"])
    except Exception as e:
        critical("Can't get project list",exc=e)

@project.command(help="Build project documentation.\n\n Arguments: \n\n PATH: project path.")
@click.argument("path",type=click.Path())
@click.option("--to","__to",type=click.Path(),default=None,help="Save built documentation to specified path")
@click.option("--open","__open", flag_value=True, default=False,help="Open the documentation in the system browser")
def make_doc(path,__to,__open):
    """ 

.. _ztc-cmd-project-make_doc:

Build Documentation
-------------------

A project can be documented in reStructuredText format and the corresponding HTML documentation can be generated by `Sphinx <http://www.sphinx-doc.org/en/1.5/>`_. The process is automated by the following command: ::

    ztc project make_doc path

where :samp:`path` is the path to the project directory.

If the command has never been run before on the project, some documentation accessory files are created. In particular:

* :file:`docs` directory inside the project
* :file:`docs/index.rst`, the main documentation file
* :file:`docs/docs.json`, a configuration file to specify the structure of the documentation. When automatically created, it contains the following fields:

    * :samp:`title`, the title of the documentation
    * :samp:`version`, not used at the moment
    * :samp:`copyright`, not used at the moment
    * :samp:`text`, used for nested json files, see below
    * :samp:`files`, a list of tuples. The second element of the tuple is the file to be scanned for documentation: the first element of the tuple is the title of the corresponding generated documentation. The file types accepted are .py, .rst and .json. File paths are specified relative to the project directory.

All files specified in :file:`docs.json` are processed:

* Python files are scanned for docstrings that are extracted to generate the corresponding .rst file inside :file:`docs`.
* rst files are included in the documentation as is
* json files must have the same structure of :file:`docs/docs.json` and generate a rst file containing the specified title, the field :samp:`text` (if given) as a preamble and a table of contents generated from the contents of the :samp:`files` field.

By default the documentation is generated in a temporary directory, but it can also be generated in a user specified directory by adding the option :option:`--to doc_path` to the command. The option :option:`--open` can be added to fire up the system browser and show the built documentation at the end of the command.

.. note:: a :file:`docs/__toc.rst` file is always generated containing the table of contents for the project documentation. It MUST be included in :file:`docs/index.rst` in order to correctly build the documentation.


    """
    docpath = fs.path(path,"docs")
    docjson = fs.path(docpath,"docs.json")
    if not __to:
        htmlpath = fs.path(fs.get_hashdir("docs"+path),"html")
    else:
        htmlpath = fs.path(__to,"html")
    info("Generating documentation at",htmlpath)
    docidx  = fs.path(docpath,"index.rst")
    if not fs.exists(fs.path(path,".zproject")):
        warning("No project at",path)
        proj = {}
    else:
        proj = fs.get_json(fs.path(path,".zproject"))
    if not fs.exists(docpath) or not fs.exists(docjson) or not fs.exists(docidx):
        # create docs skeleton
        projtitle = proj.get("title","No title")
        fs.makedirs(docpath)
        files = fs.files(path)
        fs.set_json({
            "version":"",
            "title":projtitle,
            "files":[ [fs.rpath(fname,path)[0:-3],fs.rpath(fname,path)] for fname in files if fname.endswith(".py") ]
        },docjson)
        fs.write_file(
        "*"*len(projtitle)+"\n"+
        projtitle+"\n"+
        "*"*len(projtitle)+"\n\n"+
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
        for ff in ["zerynth.css","favicon.ico","favicon-16x16.png","favicon-32x32.png","favicon-96x96.png"]:
            fs.copyfile(fs.path(fs.dirname(__file__),ff),fs.path(htmlpath,"_static",ff))
        info("Docs built at",htmlpath)
        if __open:
            webbrowser.open("file://"+fs.path(htmlpath,"index.html"))
    else:
        error("Can't build docs!")



