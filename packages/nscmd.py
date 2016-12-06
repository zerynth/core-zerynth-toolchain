"""
.. module:: Namespaces

**********
Namespaces
**********

The Zerynth Namespace is a Database Entity used to organize all the published package owned by a Zerynth User.

Each Namespace is referred to an associated repository domain and includes packages that can be visualized and downloaded by all the other z-users (according to their repositories attributes).

Namespace Commands
==================

This module contains all Zerynth Toolchain Commands for managing Zerynth Namespace Entities.
With this commands the Zerynth Users can handle and monitor all their namespaces using the command-line interface terminal.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including argument and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Namespaces are:

* :ref:`create<Create a Namespace>`: to create a Zerynth Namespace
* :ref:`list<List Namespaces>`: to list all owned Zerynth Namespaces
    """
from base import *
import click


@cli.group(help="Manage Zerynth Namespace. This module contains all Zerynth Toolchain Commands for managing Zerynth Namespace Entities.")
def namespace():
    pass

@namespace.command(help="Create a Zerynth Namespace. \n\n Arguments: \n\n NAME: name of the z-namesace.")
@click.argument("name")
def create(name):
    """ 
Create a Namespace
==================

This command is used to create and download a new Zerynth Namespace from the command line with this syntax: ::

    Syntax:   ./ztc namespace create name
    Example:  ./ztc namespace create myNS

This command take as input the following arguments:
    * **name** (str) --> the name of the namespace (**required**)

**Errors**:
    * Missing required data
    * User Asset Limit Overflow
    * Receiving Zerynth Backend response errors

    """
    info("Creating namespace...")
    try:
        res = zpost(url=env.api.ns, data={"name":name})
        rj = res.json()
        if rj["status"] == "success":
            info("Namespace",name,"created with uid:", rj["data"]["uid"])
        else:
            error("Error in namespace creation:", rj["message"])
    except Exception as e:
        critical("Can't create namespace", exc=e)


@namespace.command("list")
def __list():
    """ 
List Namespaces
===============

This command is used to list all proper Zerynth Namespaces already compiled from the command line running: ::

    Syntax:   ./ztc namespace list
    Example:  ./ztc namespace list  

This command take no input argument.

**Errors**:
    * Receiving Zerynth Backend response errors

    """
    try:
        res = zget(url=env.api.ns)
        rj = res.json()
        if rj["status"]=="success":
            log_json(rj["data"])
        else:
            error("Can't get namespace list",rj["message"])
    except Exception as e:
        critical("Can't create namespace", exc=e)
