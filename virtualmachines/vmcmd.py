"""
.. module:: VMs

****************
Virtual Machine Commands
****************
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
This module contains all Zerynth Toolchain Commands for managing Zerynth Virtual Machine Entities.
With this commands the Zerynth User can handle all his virtual machine using the command-line interface terminal.

Every Virtual Machine can be created after a device registration; the vm will be compiled for the specific related device
and with the real time operative system and features choosen by the user.
    """
    pass

@vm.command()
@click.argument("device")
@click.argument("version")
@click.argument("rtos")
@click.option("-feat", multiple=True, type=str)
@click.option("--name", default="")
def create(device,version,rtos,feat,name):
    """ 
========================
Create a Virtual Machine
========================

This command is used to create and download a new Zerynth Virtual Machine from the command line with this syntax: ::

    Syntax:   ./ztc vm create device version rtos -feat --name
    Example:  ./ztc vm create myDev 1.0.0 chibi2 --name "myZVM"

This command invokes the :func:`create` function

.. function:: create(device, version, rtos, feat=[], name="")

**Args**:
    * **device:** argument containing the alias of the device that the user wants to virtualize (type **string** --> **required**)
    * **version:** argument containing the version of the virtual machine (type **string** --> **required**)
    * **rtos:** argument containing rtos choosen by the user for the virtual machine (type **string** --> **required**)
    * **feat:** argument containing the extra features choosen by the user (only pro) for the virtual machine (type **array/multivalue** --> **optional**)
    * **name:** argument containing the name of the virtual machine (type **string** --> **optional**)

This function returns several log messages to inform the user about the results of the operation. 

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
==========================
Download a Virtual Machine
==========================

This command is used to download an existing Zerynth Virtual Machine from the command line with this syntax: ::

    Syntax:   ./ztc vm download uid version
    Example:  ./ztc vm download 3Ss_HOgpQGW7oKtYmNESPQ r1.0.0

The uid of an already compiled and available virtual machine can be found under .Zerynth/vms folder or
executing the :func:`list` function described in the next section.
This command invokes the :func:`download` function

.. function:: downlaod(uid, version)

**Args**:
    * **uid:** argument containing the uid of the virtual machine (type **string** --> **required**)
    * **version:** argument containing the version of the virtual machine (type **string** --> **required**)

This function returns several log messages to inform the user about the results of the operation. 

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
=====================
List Virtual Machines
=====================

This command is used to list all proper virtual machine already compiled from the command line with this syntax: ::

    Syntax:   ./ztc vm list --from --pretty --core_dep
    Example:  ./ztc vm list --from 0 --pretty 

This command invokes the :func:`list` function

.. function:: list(from=0, pretty=False, core_dep=None)

**Args**:
    * **from:** argument containing number from which display the virtual machine list (type **int** --> **optional**)
    * **pretty:** boolean flag to display output info in readble format (type **boolean** --> **optional**)
    * **core_dep:** ?

This function returns several log messages to inform the user about the results of the operation. 

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