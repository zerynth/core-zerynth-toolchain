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


List of device commands:

* :ref:`discover <ztc-cmd-device-discover>`
* :ref:`alias put <ztc-cmd-device-alias_put>`
* :ref:`register <ztc-cmd-device-register>`
* :ref:`virtualize <ztc-cmd-device-virtualize>`
* :ref:`supported <ztc-cmd-device-supported>`
* :ref:`open <ztc-cmd-device-open>`


The list of supported devices is available :ref:`here <doc-supported-boards>`

    """
from base import *
from .discover import *
import click
import re
import base64




_dsc = None

@cli.group(help="Manage devices.")
def device():
    global _dsc
    _dsc = Discover()

##### DEVICE ALIAS [PUT|DEL]

@device.group(help="Manage device aliases")
def alias():
    pass


@device.command(help="Discover connected devices.")
@click.option("--loop","loop",flag_value=True, default=False,help="Set continuous discover mode.")
@click.option("--looptime",default=2000,help="Set polling delay for discover")
@click.option("--matchdb","matchdb",flag_value=True, default=False,help="Match raw device data with device db.")
def discover(loop,looptime,matchdb):
    """ 
.. _ztc-cmd-device-discover:

Discover
--------

Device discovery is performed by interrogating the operative system database for USB connected peripherals. Each peripheral returned by the system has at least the following "raw" attributes:

* :samp:`vid`, the USB vendor id
* :samp:`pid`, the USB product id
* :samp:`sid`, the unique identifier assigned by the operative system, used to discriminate between multiple connected devices with the same :samp:`vid:pid`
* :samp:`port`, the virtual serial port used to communicate with the device, if present
* :samp:`disk`, the mount point of the device, if present
* :samp:`uid`, a unique identifier assigned by the ZTC
* :samp:`desc`, the device description provided by the operative system (can differ between different platforms)

Raw peripheral data can be obtained by running: ::

    ztc device discover

.. note:: In Linux peripheral data is obtained by calling into libudev functions. In Windows the WMI interface is used. In Mac calls to ioreg are used.

Raw peripheral data are not so useful apart from checking the effective presence of a device. To obtain more useful data the option :option:`-- matchdb` must be provided. Such option adds another step of device discovery on top of raw peripheral data that is matched against the list of supported devices and the list of already known devices.

A :option:`--matchdb` discovery returns a different set of more high level information:

* :samp:`name`, the name of the device taken from the ZTC supported device list
* :samp:`alias`, the device alias (if set)
* :samp:`target`, the device target, specifying what kind of microcontroller and pcb routing is to be expected on the device
* :samp:`uid`, the device uid, same as raw peripheral data
* :samp:`chipid`, the unique identifier of the device microcontrolloer (if known)
* :samp:`remote_id`, the unique identifier of the device in the Zerynth backend (if set)
* :samp:`classname`, the Python class in charge of managing the device

All the above information is needed to make a device usable in the ZTC. The information provided helps in distinguishing different devices with different behaviours. A device without an :samp:`alias` is a device that is not yet usable, therefore an alias must be :ref:`set <ztc-cmd-device-alias_put>`. A device without :samp:`chipid` and :samp:`remote_id` is a device that has not been :ref:`registered <ztc-cmd-device-register> yet and can not be virtualized yet.

To complicate the matter, there are additional cases that can be spotted during discovery:

1. A physical device can match multiple entries in the ZTC supported device list. This happens because often many different devices are built with the same serial USB chip and therefore they all appear as the same hardware to the operative system. Such device are called "ambiguous" because the ZTC can not discriminate their :samp:`target`. For example, both the Mikroelektronika Flip&Click development board and the Arduino Due, share the same microcontroller and the same USB to serial converter and they both appear as a raw peripheral with the same :samp:`vid:pid`. The only way for the ZTC to differentiate between them is to ask the user to set the device :samp:`target`. For ambiguous devices the :samp:`target` can be set while setting the :samp:`alias`. Once the :samp:`target` is set, the device is disambiguated and subsequent discovery will return only one device with the right :samp:`target`.
2. A physical device can appear in two or more different configurations depending on its status. For example, the Particle Photon board has two different modes: the DFU modes in which the device can be flashed (and therefore virtualized) and a "normal" mode in which the device executes the firmware (and hence the Zerynth bytecode). The device appears as a different raw peripherals in the two modes with different :samp:`vid:pid`. In such cases the two different devices will have the same :samp:`target` and, once registered, the same :samp:`chipid` and :samp:`remote_id`. They will appear to the Zerynth backend as a single device (same :samp:`remote_id`), but the ZTC device list will have two different devices with different :samp:`alias` and different :samp:`classname`. The :samp:`classname` for such devices can be set while setting the alias. In the case of the Particle Photon, the :samp:`classname` will be "PhotonDFU" for DFU mode and "Photon" for normal mode. PhotonDFU is the :samp:`alter_ego` of Photon in ZTC terminology.
3. Some development boards do not have USB circuitry and can be programmed only through a JTAG or an external usb-to-serial converter. Such devices can not be discovered. To use them, the programmer device (JTAG or usb-to-serial) must be configured by setting :samp:`alias` and :samp:`target` to the ones the development device.

Finally, the :command:`discover` command can be run in continuous mode by specifying the option :option:`--loop`. With :option:`--loop` the command keeps printing the set of discovered devices each time it changes (i.e. a new device is plugged or a connected device is unplugged). In some operative system the continuous discovery is implemented by polling the operative system device database for changes. The polling time can be set with option :option:`--looptime milliseconds`, by default it is 2000 milliseconds.

    """
    try:
        _dsc.run(loop,looptime,matchdb)
    except Exception as e:
        warning("Exception while discovering devices:",str(e))


@alias.command("put", help="assign an unique alias to a device. \n\n Arguments: \n\n UID: device uid. \n\n ALIAS: device alias. \n\n TARGET: device target.")
@click.argument("uid")
@click.argument("alias")
@click.argument("target")
@click.option("--name",default=False,help="Set device name.")
@click.option("--chipid",default="")
@click.option("--remote_id",default="")
@click.option("--classname",default="",help="Set device classname.")
def alias_put(uid,alias,name,target,chipid,remote_id,classname):
    """ 
.. _ztc-cmd-device-alias_put

Device configuration
--------------------

Before usage a device must be configured. The configuration consists in linking a physical device identified by its :samp:`uid` to a logical device identified by its :samp:`alias` and :samp:`target` attributes. Additional attributes can be optionally set.
The configuration command is: ::

    ztc device alias put uid alias target

where :samp:`uid` is the device hardware identifier (as reported by the discovery algorithm), :samp:`alias` is the user defined device name (no spaces allowed) and :samp:`target` is one of the supported the :ref:`supported <ztc-cmd-device-supported>` devices target. A :samp:`target` specifies what kind of microcontroller, pin routing and additional perpherals can be found on the device. For example, the :samp:`target` for NodeMCU2 development board id :samp:`nodemcu2` and informs the ZTC about the fact that the configured device is a NodeMCU2 implying an esp8266 microcontroller, a certain pin routing and an onboard FTDI controller. 

There is no need to write the whole :samp:`uid` in the command, just a few initial character suffice, as the list of known uids is scanned and compared to the given partial :samp:`uid` (may fail if the given partial :samp:`uid` matches more than one uid).

Additional options can be given to set other device attributes:

* :option:`--name name` set the human readable device name to :samp:`name` (enclose in double quotes if the name contains spaces)
* :option:`--chipid chipid` used by external tools to set the device :samp:`chipid` manually
* :option:`--remote_id remote_id` used by external tools to set device :samp:`remote_id` manually
* :option:`--classname classname` used to set the device :samp:`classname` in case of ambiguity.

Aliases can be also removed from the known device list with the command: ::

    ztc device alias del alias



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


@alias.command("del", help="Delete a device from the known device list. \n\n Arguments: \n\n ALIAS: The alias of the device to remove.")
@click.argument("alias")
def alias_del(alias):
    env.del_dev(Var({"alias":alias}))



#TODO: remove
def _target_exists(target):
    if not target: return False
    for k,v in _dsc.device_cls.items():
        if "target" in v and v["target"]==target:
            return True
    return False

@device.command(help="Register a new device. \n\n Arguments: \n\n ALIAS: device alias")
@click.argument("alias")
def register(alias):
    """ 
.. _ztc-cmd-device-register:

Device Registration
-------------------

To obtain a virtual machine a device must be registered first. The registration process consists in flashing a registration firmware on the device, obtaining the microcontroller unique identifier and communicating it to the Zerynth backend.
The process is almost completely automated, it may simply require the user to put the device is a mode compatible with burning firmware.

Device registration is performed by issuing the command: ::

    ztc device register alias

where :samp:`alias` is the device alias previously set (or just the initial part of it).

The result of a correct registration is a device with the registration firmware on it, the device :samp:`chipid` and the device :samp:`remote_id`. Such attributes are automatically added to the device entry in the known device list.

.. note:: Devices with multiple modes can be registered one at a time only!

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
.. _ztc-cmd-device-virtualize:

Virtualization
--------------

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



