"""
.. _ztc-cmd-vm:

****************
Virtual Machines 
****************

Virtual machines are the core of Zerynth. From the point of view of the ZTC, a virtual machine is a binary blob to be flashed on a device
in order to enable Zerynth code execution. Virtual machines are tied to the unique identifier of the device microcontroller, therefore for each microcontroller a specific virtual machine must be created.

Virtual machines can be managed with the following commands:

* :ref:`create <ztc-cmd-vm-create>`
* :ref:`list <ztc-cmd-vm-list>`
* :ref:`available <ztc-cmd-vm-available>`
* :ref:`bin <ztc-cmd-vm-bin>`

    """
from base import *
from packages import *
import click
import datetime
import json
import sys
import base64


def download_vm(uid):
    res = zget(url=env.api.vm+"/"+uid)
    rj = res.json()
    if rj["status"]=="success":
        vmd = rj["data"]
        vmpath = fs.path(env.vms, vmd["dev_type"],vmd["on_chip_id"])
        fs.makedirs(vmpath)
        vmname = uid+"_"+vmd["version"]+"_"+vmd["hash_features"]+"_"+vmd["rtos"]+".vm"
        fs.set_json(vmd, fs.path(vmpath,vmname))
        info("Downloaded Virtual Machine in", vmpath,"with uid",uid)
    else:
        fatal("Can't download virtual machine:", rj["message"])


@cli.group(help="Manage Zerynth Virtual Machine. This module contains all Zerynth Toolchain Commands for managing Zerynth Virtual Machine Entities.")
def vm():
    pass

@vm.command(help="Request virtual machine creation. \n\n Arguments: \n\n ALIAS: device alias. \n\n VERSION: requested virtual machine version. \n\n RTOS: virtual machine RTOS.")
@click.argument("alias")
@click.argument("version")
@click.argument("rtos")
@click.argument("patch")
@click.option("--feat", multiple=True, type=str,help="add extra features to the requested virtual machine (multi-value option)")
@click.option("--name", default="",help="Virtual machine name")
def create(alias,version,rtos,feat,name,patch):
    """ 

.. _ztc-cmd-vm-create:

Create a Virtual Machine
------------------------

Virtual machine can be created with custom features for a specific device. Creation consists in requesting a virtual machine unique identifier (:samp:`vmuid`) to the Zerynth backend for a registered device.

The command: ::

    ztc vm create alias version rtos patch

executes a REST call to the Zerynth backend asking for the creation of a virtual machine for the registered device with alias :samp:`alias`. The created virtual machine will run on the RTOS specified by :samp:`rtos` using the virtual machine release version :samp:`version` at patch :samp:`patch`.

It is also possible to specify the additional option :option:`--feat feature` to customize the virtual machine with :samp:`feature`. Some features are available for pro accounts only. Multiple features can be specified repeating the option.

If virtual machine creation ends succesfully, the virtual machine binary is also downloaded and added to the local virtual machine storage. The :samp:`vmuid` is printed as a result.

    """
    dev = env.get_dev_by_alias(alias)
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
        "patch":patch,
        "features": feat
        }
    _vm_create(vminfo)



def _vm_create(vminfo):
    info("Creating vm for device",vminfo["dev_uid"])
    try:
        res = zpost(url=env.api.vm, data=vminfo,timeout=20)
        rj = res.json()
        if rj["status"] == "success":
            vminfo["uid"]=rj["data"]["uid"]
            info("VM",vminfo["name"],"created with uid:", vminfo["uid"])
            download_vm(vminfo["uid"])
        else:
            critical("Error while creating vm:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't create vm", exc=e)

@vm.command(help="Request virtual machine creation given device uid")
@click.argument("dev_uid")
@click.argument("version")
@click.argument("rtos")
@click.argument("patch")
@click.option("--feat", multiple=True, type=str,help="add extra features to the requested virtual machine (multi-value option)")
@click.option("--name", default="",help="Virtual machine name")
def create_by_uid(dev_uid,version,rtos,feat,name,patch):
    vminfo = {
        "name": "dev:"+dev_uid,
        "dev_uid":dev_uid,
        "version": version,
        "rtos": rtos,
        "patch":patch,
        "features": feat
        }
    _vm_create(vminfo)




@vm.command("list", help="List all owned virtual machines")
@click.option("--from","_from",default=0,help="skip the first n virtual machines")
@click.option("--dev_uid","_dev_uid",default=None,help="ask for specific device")
def __list(_from, _dev_uid):
    """ 
.. _ztc-cmd-vm-list:

List Virtual Machines
---------------------

The list of created virtual machines can be retrieved with the command: ::

    ztc vm list

The retrieved list contains at most 50 virtual machines.

Additional options can be provided to filter the returned virtual machine set:

* :option:`--from n`, skip the first :samp:`n` virtual machines
* :option:`--dev_uid`, ask vm list for a specific device

    """
    table=[]
    try:
        prms = {
            "from":_from,
            "dev_uid": _dev_uid
        }
        prms["version"]=env.var.version
        res = zget(url=env.api.vm,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            if env.human:
                for k in rj["data"]["list"]:
                    table.append([_from,k["uid"],k["name"],k["version"],k["patch"],k["dev_type"],k["rtos"],k["features"]])
                    _from += 1
                log_table(table,headers=["Number","UID","Name","Version","Patch","Dev Type","Rtos","Features"])
            else:
                log_json(rj["data"])                
        else:
            critical("Can't get vm list",rj["message"])
    except Exception as e:
        critical("Can't get vm list",exc=e)

@vm.command(help="List available virtual machine parameters. \n\n Arguments: \n\n TARGET: target of the virtual machine")
@click.argument("target")
def available(target):
    """ 
.. _ztc-cmd-vm-available:

Virtual Machine parameters
--------------------------

For each device target a different set of virtual machines can be created that takes into consideration the features of the hardware. Not every device can run every virtual machine. The list of available virtual machines for a specific target can be retrieved by: ::

    ztc vm available target

For the device target, a list of possible virtual machine configurations is returned with the following attributes:

* virtual machine version 
* RTOS
* additional features
* free/pro only

    """
    table=[]
    try:
        res = zget(url=env.api.vmlist+"/"+target+"/"+env.var.version)
        rj = res.json()
        if rj["status"]=="success":
            if env.human:
                vmt = rj["data"]["vms"]
                for patch in rj["data"]["patches"]:
                    if patch not in vmt:
                        #skip 
                        continue
                    for vm in vmt[patch]:
                        table.append([vm["title"],vm["description"],vm["rtos"],vm["features"],"Premium" if vm["pro"] else "Starter",env.var.version,patch])
                log_table(table,headers=["Title","Description","Rtos","Features","Type","Version","Patch"])
            else:
                log_json(rj["data"])
        else:
            fatal("Can't get vm list",rj["message"])
    except Exception as e:
        critical("Can't retrieve available virtual machines",exc=e)

@vm.command("bin", help="Convert a VM to binary format")
@click.argument("uid")
@click.option("--path", default="",help="Path for bin file")
def __bin(uid, path):
    """ 
.. _ztc-cmd-vm-bin:

Virtual Machine Binary File
---------------------------

The binary file(s) of an existing virtual machine can be obtained with the command: ::

    ztc vm bin uid

where :samp:`uid` is the unique identifier of the virtual machine

Additional options can be provided:

* :option:`--path path` to specify the destination :samp:`path`

    """
    vm_file = None
    vm_file = tools.get_vm_by_uid(uid)
    #print(vm_file)
    if not vm_file:
        fatal("VM does not exist, create one first")
    try:
        vmj = fs.get_json(fs.path(vm_file))
        if path:
            vmpath = path
        else:
            vmpath = fs.path(".")
        #info("Generating binary for vm:", vmj["name"], "with rtos:", vmj["rtos"], "for dev:", vmj["dev_uid"])
        if "bin" in vmj and isinstance(vmj["bin"], str):
            fs.write_file(base64.standard_b64decode(vmj["bin"]), fs.path(vmpath, "vm_"+vmj["dev_type"]+".bin"))
        elif "bin" in vmj and isinstance(vmj["bin"], list):
            for count,bb in enumerate(vmj["bin"]):
                fs.write_file(base64.standard_b64decode(bb), fs.path(vmpath, "vm_"+vmj["dev_type"]+"_part_"+str(count)+".bin"))
        info("Created vm binary in", vmpath)
    except Exception as e:
        fatal("Generic Error", e)

@vm.command("reg", help="Convert a registering bootloader to binary format")
@click.argument("target")
@click.option("--path", default="",help="Path for bin file")
def __reg(target, path):
    """ 
.. _ztc-cmd-vm-reg:

Registering Binary File
-----------------------

The binary file(s) of a a registering bootloader can be obtained with the command: ::

    ztc vm reg target

where :samp:`target` is the name of the device to register.

Additional options can be provided:

* :option:`--path path` to specify the destination :samp:`path`

    """
    reg_file = fs.path(env.devices,target,"register.vm")
    if not reg_file:
        fatal("No such target",target)
    try:
        vmj = fs.get_json(reg_file)
        if path:
            vmpath = path
        else:
            vmpath = fs.path(".")
        info("Generating binary...")
        if "bin" in vmj and isinstance(vmj["bin"], str):
            fs.write_file(base64.standard_b64decode(vmj["bin"]), fs.path(vmpath, "reg_"+target+".bin"))
        elif "bin" in vmj and isinstance(vmj["bin"], list):
            for count,bb in enumerate(vmj["bin"]):
                fs.write_file(base64.standard_b64decode(bb), fs.path(vmpath, "reg_"+target+"_part_"+str(count)+".bin"))
    except Exception as e:
        fatal("Generic Error", e)




