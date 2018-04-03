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
import re
import struct

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
def __list(_from,_dev_uid):
    """ 
.. _ztc-cmd-vm-list:

List Virtual Machines
---------------------

The list of created virtual machines can be retrieved with the command: ::

    ztc vm list

The retrieved list contains at most 50 virtual machines.

Additional options can be provided to filter the returned virtual machine set:

* :option:`--from n`, skip the first :samp:`n` virtual machines

    """
    table=[]
    try:
        prms = {"from":_from}
        prms["version"]=env.var.version
        prms["dev_uid"]=_dev_uid
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



################# CUSTOM VMs

@vm.group(help="Manage custom virtual machines.")
def custom():
    pass


@custom.command("create")
@click.argument("target")
@click.argument("short_name")
@click.argument("outdir")
def _custom_template(target,short_name,outdir):
    dev = tools.get_target(target)
    if not dev:
        fatal("Target does not exists!")
    if not dev.customizable:
        fatal("Target does not support custom VMs!")
    if short_name.count("_")>1:
        fatal("Too many underscores in the given short_name!")
    if len(short_name)>31:
        fatal("short_name too long! max 31 ascii chars allowed...")
    tdir = fs.path(env.devices,target)
    ddir = fs.path(env.cvm,short_name)
    fs.copytree(tdir,ddir)
    djf = fs.path(ddir,"device.json") 
    yjf = fs.path(ddir,"template.yml")
    pjf = fs.path(ddir,short_name+".py")
    dj = fs.get_json(djf)
    #update device.json fields
    djname = short_name+"Device" 
    oldname = dj["virtualizable"]
    dj["target"]=short_name
    dj["classes"]=[short_name+"."+djname]
    dj["virtualizable"]=djname
    dj["jtag_class"]=djname
    
    tmpl = fs.get_yaml(yjf)
    # add device info to template
    tmpl["device"]=dj

    # rename device class
    fs.move(fs.path(ddir,target+".py"),pjf)
    txt = fs.readfile(pjf)
    txt = txt.replace(oldname,djname)
    fs.write_file(txt,pjf)
    # update device.json
    fs.set_json(dj,djf)
    # update base template
    fs.set_yaml(tmpl,yjf)

    # save template in outdir for compilation
    fs.set_yaml(tmpl,fs.path(outdir,short_name+".yml"))

        
@custom.command("compile")
@click.argument("template")
def _custom_compile(template):
    tmpl = fs.get_yaml(template)
    short_name = tmpl["short_name"]
    cvm_dir = fs.path(env.cvm,short_name)
    if not fs.exists(cvm_dir):
        fatal("Custom device does not exist yet! Run the create command first...")
    cvm_tmpl = fs.path(cvm_dir,short_name+".yml")
    cvm_port = fs.path(cvm_dir,"port.yml")
    cvm_bin = fs.path(cvm_dir,"port.bin")
    cvm_dev = fs.path(cvm_dir,"device.json")
    
    # generate cvm files:
    # - yaml original template
    # - yaml file for compiler
    # - binary cvminfo

    info("Saving binary template @",cvm_bin)
    _custom_generate(tmpl,cvm_port,cvm_bin)
    info("Saving original template @",cvm_tmpl)
    fs.copyfile(template,cvm_tmpl) 
    info("Saving device info @",cvm_dev)
    fs.set_json(tmpl["device"],cvm_dev)
    info("Activating custom vm")
    fs.set_json({},fs.path(cvm_dir,"active"))
    info("Done")



@custom.command("list")
def _custom_list():
    lst = []
    for d in fs.dirs(env.cvm):
        ff = fs.path(d,"active")
        if fs.exists(ff):
            lst.append({
                "target":fs.basename(d)
            })
    log_json(lst)
            
##################

_classes = {
    "D":0x0000,
    "A":0x0100,
    "ADC":0x0100,
    "SPI":0x0200,
    "I2C":0x0300,
    "PWM":0x0400,
    "ICU":0x0500,
    "CAN":0x0600,
    "SER":0x0700,
    "DAC":0x0800,
    "LED":0x0900,
    "BTN":0x0A00
}

_classes_id = {
    0x01: "ADC",
    0x02: "SPI",
    0x03: "I2C",
    0x04: "PWMD",
    0x05: "ICUD",
    0x06: "CAN",
    0x07: "SERIAL",
    0x08: "DAC",
    0x09: "LED",
    0x0A: "BTN",
    0x0D: "HTM",
    0x0E: "RTC"
    }

_flags = {
    "SPI":1<<0x02,
    "I2C":1<<0x03,
    "SER":1<<0x07,
    "CAN":1<<0x06,
    "PWM":1<<0x04,
    "ICU":1<<0x05,
    "ADC":1<<0x01,
    "DAC":1<<0x08,
    "EXT":1<<0x00
}

_prphs = {
    "SER":0x700,
    "SPI":0x0200,
    "I2C":0x0300,
    "ADC":0x0100,
    "PWMD":0x0400,
    "ICUD":0x0500,
    "CAN":0x0600,
    "SD":0x0C00,
    "RTC":0x2000
}

_names = {
    "SPI":["MOSI","MISO","SCLK"],
    "I2C":["SDA","SCL"],
    "SER":["RX","TX"],
    "CAN":["CANRX","CANTX"],
    "PWM":["PWM"],
    "ICU":["ICU"],
    "ADC":["A"],
    "DAC":["DAC"],
    "BTN":["BTN"],
    "LED":["LED"]
}

_s_classes = {
    "ADC": "_analogclass",
    "SPI": "_spiclass",
    "I2C": "_i2cclass",
    "PWM": "_pwmclass",
    "ICU": "_icuclass",
    "CAN": "_canclass",
    "DAC": "_dacclass",
    "LED": "_ledclass",
    "BTN": "_btnclass"
}

_ports = {
    "PA":0,
    "PB":1,
    "PC":2,
    "PD":3,
    "PE":4,
    "PF":5,
    "PG":6,
    "PH":7
}

_psplitter = re.compile("([A-Z]+)([0-9]+)")

def get_pin_class(pinname):
    mth = _psplitter.match(pinname)
    if not mth:
        return ""
    pin = mth.group(1)
    num = int(mth.group(2))
    for cls,cls_names in _names.items():
        if pin in cls_names:
            return cls

    return ""

def get_prph(prph):
    if prph.startswith("I2C"):
        return prph[0:3],int(prph[3:])
    mth = _psplitter.match(prph)
    if not mth:
        return "",-1
    return mth.group(1),int(mth.group(2))

def _get_sorted_classes(tbl,cls):
    if cls in ["SPI","I2C","SER"]:
        ret = []
        if cls=="SER":
            n = len(tbl)//2
            for i in range(n):
                ret.append("RX"+str(i))
                ret.append("TX"+str(i))
        elif cls=="SPI":
            n = len(tbl)//3
            for i in range(n):
                ret.append("MOSI"+str(i))
                ret.append("MISO"+str(i))
                ret.append("SCLK"+str(i))
        elif cls=="I2C":
            n = len(tbl)//2
            for i in range(n):
                ret.append("SDA"+str(i))
                ret.append("SCL"+str(i))
        return ret
    else:
        return sorted(tbl)

def _get_pin_code(pin):
    mth = _psplitter.match(pin)
    if not mth:
        return -1
    pin = mth.group(1)
    num = int(mth.group(2))
    if pin=="RX":
        return 0x0700+2*num
    elif pin=="TX":
        return 0x0701+2*num
    elif pin=="SDA":
        return 0x0300+2*num
    elif pin=="SCL":
        return 0x0301+2*num
    elif pin=="MOSI":
        return 0x0200+3*num
    elif pin=="MISO":
        return 0x0201+3*num
    elif pin=="SCLK":
        return 0x0202+3*num
    return -1

def _pad_to(bb,pad=16):
    if len(bb)%pad==0:
        return bb
    padding = pad - len(bb)%pad
    bb.extend(b'\x00'*padding)
    return bb


# @custom.command("compile")
# @click.argument("template")
# @click.argument("outdir")
def _custom_generate(tmpl,ymlfile,binfile):
    short_name = tmpl["short_name"]
    port = {}
    pinmap = tmpl["pinmap"]
    pinclasses = tmpl["pinclasses"]
    peripherals = tmpl["peripherals"]
    
    pin_names = ["D"+str(i) for i in range(0,256)]
    npins = len(pinmap)
    cls_table = {}
    prph_table = {}
    vbl_table = {}
    prphs = set()

    for i in range(npins):
        pin = "D"+str(i)
        pindata = pinmap.get(pin)
        if not pindata or len(pindata)!=2:
            fatal("Missing pinmap for pin", pin)
        pindata.append(set([1])) # prepare space for flags: add ext
        
        
    # search pin attributes
    # fill pinmap with pin classes
    # create pinclasses lists
    for pc, pv in pinclasses.items():
        cls = get_pin_class(pc)
        if not cls:
            fatal("Bad pin name in pinclasses section:",pc)
        
        # build class tables
        if cls not in cls_table:
            cls_table[cls]={}
        
        if pc in cls_table[cls]:
            fatal("Duplicate pin!",pc)
        
        if isinstance(pv,str):
            thepin = pv
            thepindata = [pv, 0, 0, 0]
        elif isinstance(pv,list):
            pv.extend( (4-len(pv))*[0])  
            thepindata = pv
            thepin = pv[0]
        else:
            fatal("Bad format: expected list or string at",pc)

        # add pinflags
        if cls in _flags:
            pinmap.get(thepin)[2].add(_flags[cls])
        # add pindata to classes
        cls_table[cls][pc]=thepindata

    for prph, prph_info in peripherals.items():
        prp, num = get_prph(prph)
        if num<0:
            fatal("unknown perpheral",prph)
        if prp not in prph_table:
            prph_table[prp]={}
            vbl_table[prp]=set()
        prph_table[prp][num]=prph_info["hw"]
        prphs.add(prph)
        if prp=="SERIAL":
            vbl_table[prp].add((num,prph_info["rx"],prph_info["tx"]))
        elif prp=="SPI":
            vbl_table[prp].add((num,prph_info["mosi"],prph_info["miso"],prph_info["sclk"]))
        elif prp=="I2C":
            vbl_table[prp].add((num,prph_info["sda"],prph_info["scl"]))
        else:
            vbl_table[prp].add(num)

    # add implicit peripherals

    if "A0" in pinclasses:
        prph_table["ADC"]=1
        prphs.add("ADC0")
    if "PWM0" in pinclasses:
        prph_table["PWMD"]=1
        prphs.add("PWMD0")
    if "ICU0" in pinclasses:
        prph_table["ICUD"]=1
        prphs.add("ICUD0")
    if "DAC0" in pinclasses:
        prph_table["DAC"]=1
        prphs.add("DAC0")


    # generate port.yml ~ port.def
   
    prphs = list(prphs)
    prphs.sort()

    port["defines"]={
        "LAYOUT":  tmpl.get("layout",short_name),
        "BOARD":short_name,
        "CDEFS": tmpl.get("cmacros",[])
    }
    names = set()
    for pin in pinmap:
        names.add(pin)
    for pin in pinclasses:
        names.add(pin)
    for prph in prphs:
        names.add(prph)
    port["peripherals"]=[x for x in prphs]
    port["names"]=list(names)
    pinout = {}
    for pin in pinmap:
        pinout[pin]={}
        for pc, pv in pinclasses.items():
            if isinstance(pv,list):
                pv=pv[0]
            if pv==pin:
                mth = _psplitter.match(pc)
                pinout[pin][mth.group(1)]=pc
                if mth.group(1)=="A":
                    pinout[pc]={"ADC":pc}

    port["pinout"]=pinout
                

    # generate port.bin

    header = bytearray()
    body = bytearray()

    # c prefix is for PinClass* structures
    # m prefix is for vhal_prph_map structures
    # v prefix is for vbl structures

    # set offsets to 0
    c_offsets = [0]*16
    # set table sizes to 0
    c_sizes = [0]*16
    # set offsets to 0
    m_offsets = [0]*16
    # set table sizes to 0
    m_sizes = [0]*16
    # set offsets to 0
    v_offsets = [0]*16
    # set table sizes to 0
    v_sizes = [0]*16

    # generate binary pinmap
    bmap = bytearray()
    for pin in pin_names:
        if pin not in pinmap:
            break
        pindata = pinmap[pin]
        pp = _ports[pindata[0]]
        pn = pindata[1]
        pf = sum(pindata[2])
        bmap.extend(struct.pack("<B",pp)+struct.pack("<B",pn)+struct.pack("<H",pf))

    
    # generate peripheras maps and classes
    mmap = {}
    cmap = {}
    for cid in sorted(_classes_id):
        cname = _classes_id[cid]
        if cname not in prph_table:
            # not defined
            continue
        cdata = prph_table[cname]
        if isinstance(cdata,int):
            cdata = {0:1}
        bbmap = bytearray()
        for k in sorted(cdata):
            bbmap.extend(struct.pack("<B",cdata[k]))
        mmap[cid] = bbmap
        m_sizes[cid] = len(cdata)

        # ugly, but necessary: convert long prph to short prph
        if cname in ["PWMD","ICUD","SERIAL"]:
            cname = cname[0:3]
        if cname not in cls_table:
            #skip peripherals without pins: HTM,RTC,...
            continue
        # set classes
        tbl = cls_table[cname]
        cmap[cid]=bytearray()
        for pn in _get_sorted_classes(tbl, cname):
            pdata = tbl[pn]
            pdata[0]=int(pdata[0][1:]) #strip the D
            cmap[cid].extend(struct.pack("<4B",*pdata))
        c_sizes[cid] = len(tbl) 

    # generate vbl maps; TODO: make it general when more vbl maps will be needed
    vmap={}
    for mn,mt in [(0x07,"SERIAL"),(0x03,"I2C"),(0x02,"SPI")]:
        lst = sorted(vbl_table[mt])
        v_sizes[mn]=len(lst)
        vmap[mn]=bytearray()
        for pdata in lst:
            for pd in pdata:
                if isinstance(pd,int):
                    #skip index
                    continue
                vmap[mn].extend(struct.pack("<H",_get_pin_code(pd)))
            if mt=="SPI":
                #add 0 padding for SPI: TODO remove when not more needed
                vmap[mn].extend(b'\x00\x00')


    
    #build the full cvm structure 

    #begin with pinmap
    c_offsets[0]=0
    c_sizes[0]=len(pinmap)  # NUM_PINS
    body.extend(bmap)
    _pad_to(body)

    # now fill with classes
    for cid in sorted(_classes_id):
        cname = _classes_id[cid]
        if cname not in prph_table:
            # not defined, set to 0
            continue
        if cid not in cmap:
            continue
        c_offsets[cid]=len(body)
        body.extend(cmap[cid])
        _pad_to(body)

    # now fill prph maps
    for cid in sorted(_classes_id):
        cname = _classes_id[cid]
        if cname not in prph_table:
            # not defined, set to 0
            continue
        m_offsets[cid]=len(body)
        body.extend(mmap[cid])
        _pad_to(body)

    # now fill vbl maps
    for mn in [0x07,0x03,0x02]:
        v_offsets[mn] = len(body)
        body.extend(vmap[mn])
        _pad_to(body)


    # set header parameters
    header.extend(struct.pack("<H",len(body))) #size
    header.extend(struct.pack("<H",1)) #version
    # set offsets
    header.extend(struct.pack("<16H",*c_offsets))
    header.extend(struct.pack("<16H",*m_offsets))
    header.extend(struct.pack("<16H",*v_offsets))
    # set sizes
    header.extend(struct.pack("<16B",*c_sizes))
    header.extend(struct.pack("<16B",*m_sizes))
    header.extend(struct.pack("<16B",*v_sizes))
    #set target name
    header.extend(struct.pack("32s",short_name.encode("ascii")))
    #set target size
    header.extend(struct.pack("<H",len(short_name)))
    #add padding
    header.extend(struct.pack("<10B",*([0]*10)))



    bin = header+body

    debug("Header size:         ",len(header),hex(len(header)))
    debug("Header.size:         ",hex(struct.unpack("<H",header[0:2])[0]))
    debug("Header.version:      ",hex(struct.unpack("<H",header[2:4])[0]))
    debug("Header.c_offsets:    ",[ hex(x) for x in struct.unpack("<16H",header[4:4+32])])
    debug("Header.c_sizes:      ",[ hex(x) for x in struct.unpack("<16B",header[4+96:4+112])])
    debug("Header.m_offsets:    ",[ hex(x) for x in struct.unpack("<16H",header[4+32:4+64])])
    debug("Header.m_sizes:      ",[ hex(x) for x in struct.unpack("<16B",header[4+112:4+128])])
    debug("Header.v_offsets:    ",[ hex(x) for x in struct.unpack("<16H",header[4+64:4+96])])
    debug("Header.v_sizes:      ",[ hex(x) for x in struct.unpack("<16B",header[4+128:4+144])])
    debug("Header.target:       ",struct.unpack("32s",header[4+144:4+176])[0])
    debug("Header.target_size:  ",struct.unpack("<H",header[4+176:4+178])[0])

    # ymlfile = fs.path(outdir,"port.yml")
    # binfile = fs.path(outdir,"port.bin")

    fs.set_yaml(port,ymlfile)
    fs.write_file(bin,binfile)
    






