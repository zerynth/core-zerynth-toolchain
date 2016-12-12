"""
.. _ztc-cmd-device:

*******
Devices
*******

In the ZTC a device is a peripheral that can execute Zerynth bytecode. In order to do so a device must be prepared and customized with certain attributes.
The main attributes of a device are:

* :samp:`alias`, a unique name given by the user to the device in order to identify it in ZTC commands
* :samp:`uid`, a unique id provided by the operative system identifying the device at hardware level
* :samp:`target`, specifies what kind of virtual machine can be run by the device
* :samp:`name`, a human readable name describing the device. Automatically set by the ZTC
* :samp:`chipid`, the unique identifier of the microcontroller present on the device
* :samp:`remote_id`, the unique identifier of the device in the pool of user registered device
* :samp:`classname`, a Python class name identifying the class containing commands to configure the device

When a new device is connected, some steps must be taken in order to make it able to run Zerynth code:

1. The device must be :ref:`discovered <ztc-cmd-device-discover>`, namely its hardware parameters must be collected (:samp:`uid`).
2. Once discovered an :samp:`alias` must be :ref:`assigned <ztc-cmd-device-alias_put>`. Depending on the type of device :samp:`target` and :samp:`classname` can be assigned in the same step.
3. The device must be :ref:`registered <ztc-cmd-device-register>` in order to create virtual machines for it (:samp:`chipid` and :samp:`remote_id` are obtained in this step)
4. The device must be :ref:`virtualized <ztc-cmd-device-virtualize>, namely a suited virtual machine must be loaded on the device microcontroller

The list of supported devices is available :ref:`here <doc-supported-boards>`

Device Commands
===============

This module contains all Zerynth Toolchain Commands for managing Zerynth Device Entities.
With this commands the Zerynth Users can register and virtualize their boards using the command-line interface terminal.

Before using a z-device, the z-users must assign to it an unique alias name creating a local database device entity.
This operation will permit to the z-users to refer to their boards for executing commands on them and 
will permit to the Zerynth Tool to auto-recognize the boards every time z-users connect to them to their pc.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Devices are:

* `alias put`_: to create a new local database device entity assigning an unique alias name
* `alias del`_: to delete a z-device referred to a specific alias name
* discover_: to discover the connected z-devices
* supported_: to list supported z-devices
* register_: to register new z-devices
* virtualize_: to virtualize a z-devices
* open_: to open serial port for the communication with the z-device

    """
from base import *
from .discover import *
import click
import re
import base64




_dsc = None

@cli.group(help="Manage Zerynth Devices.")
def device():
    global _dsc
    _dsc = Discover()

##### DEVICE ALIAS [PUT|DEL]

@device.group(help="For managing Z-Device Locally")
def alias():
    pass


#TODO test once boards are ok
@alias.command("put", help="to create a local database device entity and assign to it an unique alias name. \n\n Arguments: \n\n UID: Uid of the device found in the discover command results. \n\n ALIAS: Unique Alias Name for the device. \n\n TARGET: Target of the device.")
@click.argument("uid")
@click.argument("alias")
@click.argument("target")
@click.option("--name",default=False,help="Name of the Zerynth Device.")
@click.option("--chipid",default="")
@click.option("--remote_id",default="")
@click.option("--classname",default="",help="Classname of the Zerynth Device.")
def alias_put(uid,alias,name,target,chipid,remote_id,classname):
    """ 
.. _alias_put:

Alias Put
---------

This command is used to create a new local database device entity with a custom unique alias name from the command line with this syntax: ::

    Syntax:   ./ztc device alias put uid alias target --name --chipid --remote_id --classname
    Example:  ./ztc device alias put 776ff4bc8fdfd700ef92005c7024b3af914b86e6 uid_alias_name --name "myBoard"

This command take as input the following arguments:
    * **uid** (str) -->  the uid of the related device found in the `discover` command diplay results (**required**)
    * **alias** (str) --> the unique alias name to assign to the device (**required**)
    * **target** (str) -->  the target of the z-device (**required**)
    * **name** (str) --> the name of the z-device (**optional**, default=False)
    * **classname** (str) --> the classname of the z-device (**optional**, default="")


**Errors**:
    * Missing input required data
    * Errors on matching device target or classname (for multiclass devices) 

    """
    #if not re.match("^[A-Za-z0-9_:-]{4,}$",alias):
    #    fatal("Malformed alias")
    devs = _dsc.run_one(True)
    #print(devs)
    uids=_dsc.matching_uids(devs, uid)
    #print(uids)
    if len(uids)<=0:
        fatal("No devices with uid",uid)
    else:
        uid = uids[0]
        dd = [dev for uu,dev in devs.items() if dev.uid==uid]
        dd = dd[0]
        if not classname and len(dd["classes"])>1:
            fatal("Multiclass device! Must specify --classname option")
        if not classname:
            classname = dd["classes"][0].split(".")[1]
        aliaskey = alias
        aliases = env.get_dev(uid)
        aliasuid = aliases[alias].uid if alias in aliases else None
        if not _target_exists(target):
            fatal("No such target",target)
        ###TODO to define chipid and remote_id if needed ... related option are not documented
        deventry = {
            "alias":alias,
            "uid":uid,
            "name": aliases[alias].name if not name and aliasuid!=None else "",
            "target": target,
            "chipid":chipid,
            "remote_id":remote_id,
            "classname":classname
        }
        env.put_dev(deventry) 
        #TODO open devdb, get/set uid+unique_alias+name+shortname(this disambiguate a device)


@alias.command("del", help="to delete a z-device from the local device database. \n\n Arguments: \n\n ALIAS: The alias of the z-device.")
@click.argument("alias")
def alias_del(alias):
    """ 
.. _alias_del:

Alias Del
---------

This command is used to delete a z-device from the local database running this command from the terminal: ::

    Syntax:   ./ztc project alias del alias
    Example:  ./ztc project alias del uid_alias_name

This command take as input the following arguments:
    * **alias** (str) --> the unique alias name to assign to the device (**required**)
    
**Errors**:
    * Missing input required data
    * Wrong Alias

    """
    env.del_dev(Var({"alias":alias}))
    

@device.command(help="To discover connected devices.")
@click.option("--loop","loop",flag_value=True, default=False,help="Flag for infinity loop execution.")
@click.option("--looptime",default=2,help="Sleep time in the infinity loop in second.")
@click.option("--matchdb","matchdb",flag_value=True, default=False,help="Flag for finding matches in device db.")
def discover(loop,looptime,matchdb):
    """ 
.. _discover:

Discover Devices
----------------

This command is used to discover devices connected to the z-user pc using the command line with this syntax: ::

    Syntax:   ./ztc device discover --loop --looptime --matchdb
    Example:  ./ztc device discover --matchdb

This command take as input the following arguments:
    * **loop** (bool) --> flag to exec in infinite loop this command (**optional**, default=False)
    * **looptime** (int) --> time to sleep at the end of the loop operations (**optional**, default=2)
    * **matchdb** (bool) --> flag to enable the matching between devices connected and z-device in local database (**optional**; default=False)

    """
    try:
        _dsc.run(loop,looptime,matchdb)
    except Exception as e:
        warning("Exception while discovering devices:",str(e))


@device.command(help="List of supported Zerynth Devices.")
@click.option("--type",default="board",type=click.Choice(["board","jtag","usbtoserial"]),help="type of device [board,jtag,usbtoserial]")
def supported(type):
    """ 
.. _supported:

List of Supported Devices
-------------------------

This command is used to list supported devices from the command line with this syntax: ::

    Syntax:   ./ztc device supported --type
    Example:  ./ztc device supported --type board

This command take as input the following argument:
    * **type** (str) --> type of the device (**optional**, default=“board")

.. note:: the type of devices available are: "board", "jtag", and "usbtoserial"

    """
    table = []
    for k,v in _dsc.device_cls.items():
        if v["type"]==type:
            if env.human:
                table.append([v["target"],v["path"]])
            else:
                log_json({
                    "target":v["target"],
                    "path":v["path"]
                })
    if env.human:
        log_table(table,headers=["Target","Path"])


#TODO: remove
def _target_exists(target):
    if not target: return False
    for k,v in _dsc.device_cls.items():
        if "target" in v and v["target"]==target:
            return True
    return False

@device.command(help="To Register a new Zerynth Device. \n\n Arguments: \n\n ALIAS: The alias of the z-device.")
@click.argument("alias")
def register(alias):
    """ 
.. _register:

Register a Device
-----------------

This command is used to register a new Zerynth Device on the Zerynth Backend Database from the command line with this syntax: ::

    Syntax:   ./ztc device register alias
    Example:  ./ztc device register uid_alias_name

This command take as input the following argument:
    * **alias** (str) --> the alias od the z-device (**required**)

**Errors**:
    * Missing input required data
    * Wrong Alias
    * Receiving Zerynth Backend response errors

.. note:: This operation is needed before first virtualization of a z-device;  

    """
    tgt = _dsc.search_for_device(alias)
    if not tgt:
        fatal("Can't find device",alias)
    elif isinstance(tgt,list):
        fatal("Ambiguous alias",[x.alias for x in tgt])
    if not tgt.virtualizable:
        fatal("Device is not virtualizable! Try to put it in a virtualizable mode...")
    
    if tgt.virtualizable != tgt.classname:
        fatal("Device must be put in virtualizable mode!")

    # open register.vm
    reg = fs.get_json(fs.path(tgt.path,"register.vm"))

    # burn register.vm
    info("Starting device registration")
    res,out = tgt.burn(bytearray(base64.standard_b64decode(reg["bin"])),info)
    
    if not res:
        fatal("Can't burn bootloader!")

    alter_ego = None
    if tgt.has_alter_ego:
        alter_ego = tgt
        clsname = tgt.has_alter_ego
        uids,devs = _dsc.wait_for_classname(clsname)
        if not uids:
            fatal("Can't find this device alter ego!")
        elif len(uids)>1:
            fatal("Too many devices matching this device alter ego! Please unplug them all and retry...")
        tgt = devs[uids[0]]
    else:
        # virtualizable device is the same as uplinkable device :)
        # search for dev again and open serial
        tgt = _dsc.find_again(tgt)
        if not tgt:
            fatal("Can't find device",alias)

    conn = ConnectionInfo()
    conn.set_serial(tgt.port,**tgt.connection)
    ch = Channel(conn)
    ch.open(timeout=2)
    lines = []
    for x in range(10):
        line=ch.readline()
        lines.append(line.strip("\n"))
    ch.close()
    cnt = [lines.count(x) for x in lines]
    pos = cnt.index(max(cnt))
    if pos>=0 and cnt[pos]>3 and len(lines[pos])>=8:
        info("Found chipid:",lines[pos])
    else:
        fatal("Can't find chipid")
    chipid=lines[pos]
    # call api to register device
    dinfo = {
        "name": tgt.custom_name or tgt.name,
        "on_chip_id": chipid,
        "type": tgt.target,
        "category": tgt.family_name
    }
    try:
        res = zpost(url=env.api.devices, data=dinfo)
        rj = res.json()
        if rj["status"] == "success":
            info("Device",tgt.custom_name  or tgt.name,"registered with uid:", rj["data"]["uid"])
        else:
            fatal("Remote device registration failed with:", rj["message"])
    except Exception as e:
        critical("Error during remote registration",exc=e)
    tgt = tgt.to_dict()
    tgt["chipid"]=chipid
    tgt["remote_id"]=rj["data"]["uid"]
    env.put_dev(tgt)
    if alter_ego:
        alter_ego = alter_ego.to_dict()
        alter_ego["chipid"]=chipid
        alter_ego["remote_id"]=rj["data"]["uid"]
        env.put_dev(alter_ego)


@device.command(help="To virtualize the Zerynth Device. \n\n Arguments: \n\n ALIAS: The alias of the z-device. \n\n VMUID: The uid of the Zerynth Virtual Machine.")
@click.argument("alias")
@click.argument("vmuid")
def virtualize(alias,vmuid):
    """ 
.. _virtualize:

Virtualize a Device
-------------------

This command is used to virtualize a Zerynth Device installing on the board the real time operative system to
abilitate for running customer application code. the ``virtualize`` command has this syntax: ::

    Syntax:   ./ztc device virtualize alias vmuid
    Example:  ./ztc device virtualize uid_alias_name 3Ss_HOgpQGW7oKtYmNESPQ

This command take as input the following arguments:
    * **alias** (str) --> the alias of the z-device (**required**)
    * **vmuid** (str) --> the uid of the Zerynth Virtual Machine to load on the z-device(**required**)

**Errors**:
    * Missing required data
    * Wrong Alias
    * Wrong uid for the virtual machine

.. note:: Before virtualizing a z-device, is needed to :ref:`create<Create a Virtual Machine>` a Zerynth Virtual Machine for that specific z-device

    """
    tgt = _dsc.search_for_device(alias)
    if not tgt:
        fatal("Can't find device",alias)
    elif isinstance(tgt,list):
        fatal("Ambiguous alias",[x.alias for x in tgt])
    if tgt.virtualizable!=tgt.classname:
        fatal("Device not virtualizable")
    vms=tools.get_vms(tgt.target)
    if vmuid not in vms:
        vuids = []
        for vuid in vms:
            if vuid.startswith(vmuid):
                vuids.append(vuid)
        if len(vuids)==1:
            vmuid=vuids[0]
        elif len(vuids)>1:
            fatal("Ambiguous VM uid",vuids)
        else:
            fatal("VM",vmuid,"does not exist")
    vm = fs.get_json(vms[vmuid])
    info("Starting Virtualization...")
    res,out = tgt.burn(bytearray(base64.standard_b64decode(vm["bin"])),info)
    if not res:
        fatal("Error in virtualization")
    else:
        info("Virtualization ok")




@device.command(help="To open a serial port to communicate with the z-device. \n\n Arguments: \n\n ALIAS: The alias name of the z-device.")
@click.argument("alias")
@click.option("--echo","__echo",flag_value=True, default=False,help="Flag for printing typed characters to stdin")
def open(alias,__echo):
    """ 
.. _open:

Open a Serial Port
------------------

This command is used to open a serial port to communicate with the z-device from the command line with this syntax: ::

    Syntax:   ./ztc device open alias --echo
    Example:  ./ztc device open uid_alias_name --echo

This command take as input the following arguments:
    * **alias** (str) --> the alias name of the z-device (**required**)
    * **echo** (str) --> flag for printing typed characters to stdin (**optional**, default=False)

**Errors**:
    * Missing required data
    * Wrong Alias
    """
    tgt = _dsc.search_for_device(alias)
    if not tgt:
        fatal("Can't find device",alias)
    elif isinstance(tgt,list):
        fatal("Ambiguous alias",[x.alias for x in tgt])

    conn = ConnectionInfo()
    conn.set_serial(tgt.port,**tgt.connection)
    ch = Channel(conn,__echo)
    ch.open()
    ch.run()
    # import serial
    # ser = serial.Serial(tgt.port,115200)
    # while True:
    #     data = ser.read()
    #     log(data.decode("ascii","replace"),sep="",end="")
    #     #print(,sep="",end="")


