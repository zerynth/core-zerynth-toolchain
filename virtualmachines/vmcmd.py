"""
.. module:: VMs

****************
Virtual Machines 
****************

The Zerynth Virtual Machine is the Multi-Thread Real Time Operative System that, once installed on the related device enabled by Zerynth,
permits to the users to execute their Zerynth Projects uplinked on their device.

Every Virtual Machine can be created after a device registration and can be compiled for the specific related device
with the real time operative system and features choosen by the users.

..
"""
from base import *
import click
import datetime
import json
import sys


def download_vm(uid,version):
    res = zget(url=env.api.vm+"/"+uid+"/"+version)
    rj = res.json()
    if rj["status"]=="success":
        vmpath = fs.path(env.vms, rj["data"]["dev_type"],rj["data"]["on_chip_id"])
        fs.makedirs(vmpath)
        fs.set_json(rj["data"], fs.path(vmpath,uid+"_"+version+"_"+rj["data"]["hash_features"]+"_"+rj["data"]["rtos"]+".vm"))
        info("Downloaded Virtual Machine in", vmpath,"with uid",uid)
    else:
        fatal("Can't download virtual machine:", rj["message"])


@cli.group()
def vm():
    """
Virtual Machine Commands
========================

This module contains all Zerynth Toolchain Commands for managing Zerynth Virtual Machine Entities.
With this commands the Zerynth Users can handle all their virtual machine using the command-line interface terminal.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including argument and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Virtual Machines are:
    * :ref:`create<Create a Virtual Machine>`: to create a Zerynth Virtual Machine
    * :ref:`download<Download a Virtual Machine>`: to download an already compiled owned Zerynth Virtual Machine
    * :ref:`list<List Virtual Machines>`: to list all owned Zerynth Virtual Machines
    * :ref:`available<Retrieve a Virtual Machine>`: to retrieve a specific owned Zerynt Virtual Machine
    """
    pass

@vm.command()
@click.argument("device")
@click.argument("version")
@click.argument("rtos")
@click.option("-feat", multiple=True, type=str,help="add an axtra feature to the requested virtual machine (multivalue field)")
@click.option("--name", default="",help="name of the virtual machine")
def create(device,version,rtos,feat,name):
    """ 
Create a Virtual Machine
========================

This command is used to create and download a new Zerynth Virtual Machine from the command line with this syntax: ::

    Syntax:   ./ztc vm create device version rtos -feat --name
    Example:  ./ztc vm create myDev 1.0.0 chibi2 --name "myZVM"

This command take as input the following arguments:
    * **device** (str) --> the alias name of the device that the users want to virtualize (**required**)
    * **version** (str) --> the version of the virtual machine (**required**)
    * **rtos** (str) --> the rtos choosen by the users for the virtual machine (**required**)
    * **feat** (str, multivalue) --> the extra features choosen by the users (only pro) for the virtual machine (**optional**, default=“")
    * **name** (str) --> the name of the virtual machine (**optional**, default=“") 

**Errors**:
    * Missing required data
    * User Asset Limit Overflow
    * Bad alias for the Device
    * Rtos unsupported for the device

.. note:: The version argument of this command must following the standard versioning nomenclature.
          Available Versions: "r1.0.0", "r1.0.1"
.. warning:: Extra features not available yet

    """
    dev = env.get_dev_by_alias(device)
    if len(dev)==0:
        fatal("No such device")
    if len(dev)>1:
        fatal("Ambiguous alias")
    dev=dev[0]
    if not dev.remote_id:
        fatal("Device",dev.alias,"not registered")

    vminfo = {
        "name":name or (dev.name+" "+version),
        "dev_uid":dev.remote_id,
        "version": version,
        "rtos": rtos,
        "features": feat
        }
    info("Creating vm for device",dev.alias)
    try:
        res = zpost(url=env.api.vm, data=vminfo,timeout=20)
        rj = res.json()
        if rj["status"] == "success":
            vminfo["uid"]=rj["data"]["uid"]
            info("VM",name,"created with uid:", vminfo["uid"])
            download_vm(vminfo["uid"],vminfo["version"])
        else:
            critical("Error while creating vm:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't create vm", exc=e)


@vm.command()
@click.argument("uid")
@click.argument("version")
def download(uid,version):
    """ 
Download a Virtual Machine
==========================

This command is used to download an existing Zerynth Virtual Machine from the command line with this syntax: ::

    Syntax:   ./ztc vm download uid version
    Example:  ./ztc vm download 3Ss_HOgpQGW7oKtYmNESPQ r1.0.0

The uid of an already compiled and available virtual machine can be found under .Zerynth/vms folder or
executing the :func:`list` function described in the next section.

This command take as input the following arguments:
    * **uid** (str) --> the uid of the virtual machine (**required**)
    * **version** (str) --> the version of the virtual machine (**required**)

**Errors**:
    * Missing required data
    * Wrong uid for the virtual machine

.. note:: The version argument of this command must following the standard versioning nomenclature.
          Available Versions: "r1.0.0", "r1.0.1"

    """
    try:
        download_vm(uid,version)
    except Exception as e:
        critical("Can't download vm", exc=e)


@vm.command("list")
@click.option("--from","_from",default=0)
@click.option("--pretty","pretty",flag_value=True, default=False,help="output info in readable format")
@click.option("--core_dep",default=None)
def __list(_from,pretty,core_dep):
    """ 
List Virtual Machines
=====================

This command is used to list all proper Zerynth Virtual Machine already compiled from the command line running: ::

    Syntax:   ./ztc vm list --from --pretty --core_dep
    Example:  ./ztc vm list --from 0 --pretty 

This command take as input the following arguments:
    * **from** (int) --> the number from which display the virtual machine list (**optional**, default=0)
    * **pretty** (bool) --> flag to display the json output in readble format (**optional**, default=False)
    * **core_dep** (str) --> select the virtual machine from availables according to the related core dependency (**optional**, default=None)

**Errors**:
    * Wrong data for the virtual machine list

    """
    indent = 4 if pretty else None
    try:
        prms = {"from":_from}
        if core_dep: prms["core_dep"]=core_dep
        res = zget(url=env.api.vm,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            log(json.dumps(rj["data"],indent=indent))
        else:
            critical("Can't get vm list",rj["message"])
    except Exception as e:
        critical("Can't get vm list",exc=e)

@vm.command()
@click.argument("target")
@click.option("--pretty","pretty",flag_value=True, default=False,help="output info in readable format")
def available(target,pretty):
    """ 
Retrieve a Virtual Machine
==========================

This command is used to retrieve a specific owned Zerynth Virtual Machine informations from the command line with this syntax: ::

    Syntax:   ./ztc vm available targef --pretty
    Example:  ./ztc vm available 3Ss_HOgpQGW7oKtYmNESPQ --pretty 

This command take as input the following arguments:
    * **target** (str) --> (**requireq**)
    * **pretty** (bool) --> flag to display json output in readble format (**optional**, default=False)

**Errors**:
    * Wrong data for retriving virtual machine

    """
    indent = 4 if pretty else None
    try:
        res = zget(url=env.api.vmlist+"/"+target)
        rj = res.json()
        if rj["status"]=="success":
            log(json.dumps(rj["data"],indent=indent))
        else:
            fatal("Can't get vm list",rj["message"])
    except Exception as e:
        critical("Can't retrieve available virtual machines",exc=e)
