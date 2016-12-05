"""
.. module:: Devices

*******
Devices
*******
"""
from base import *
from .discover import *
import click
import re
import base64


_dsc = None

@cli.group()
def device():
    global _dsc
    _dsc = Discover()

@device.command()
@click.option("--loop","loop",flag_value=True, default=False,help="loop discover")
@click.option("--looptime",default=2,help="loop discover")
@click.option("--matchdb","matchdb",flag_value=True, default=False,help="find matches in device db")
def discover(loop,looptime,matchdb):
    try:
        _dsc.run(loop,looptime,matchdb)
    except:
        pass


@device.command()
@click.option("--type",default="board",type=click.Choice(["board","jtag","usbtoserial"]),help="type of device [board,jtag,usbtoserial]")
def supported(type):
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

@device.command()
@click.argument("alias")
def register(alias):
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


@device.command()
@click.argument("alias")
@click.argument("vmuid")
def virtualize(alias,vmuid):
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




@device.command()
@click.argument("alias")
@click.option("--echo","__echo",flag_value=True, default=False,help="print typed characters to stdin")
def open(alias,__echo):
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



##### DEVICE ALIAS [PUT|DEL]

@device.group()
def alias():
    pass


#TODO test once boards are ok
@alias.command("put")
@click.argument("uid")
@click.argument("alias")
@click.argument("target")
@click.option("--name",default=False)
@click.option("--chipid",default="")
@click.option("--remote_id",default="")
@click.option("--classname",default="")
def alias_put(uid,alias,name,target,chipid,remote_id,classname):
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


@alias.command("del")
@click.argument("alias")
def alias_del(alias):
    env.del_dev(Var({"alias":alias}))
    
