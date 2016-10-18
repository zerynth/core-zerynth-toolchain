from base import *
from .discover import *
import click
import re
import base64

dev_url = "http://localhost/zbackend/devices/"

_dsc = None

@cli.group()
def device():
    global _dsc
    _dsc = Discover()

@device.command()
@click.option("--loop","loop",flag_value=True, default=False,help="loop discover")
@click.option("--looptime",default=2,help="loop discover")
@click.option("--matchdb","matchdb",flag_value=True, default=False,help="find matches in device db")
@click.option("--pretty","pretty",flag_value=True, default=False,help="pretty json")
def discover(loop,looptime,matchdb,pretty):
    _dsc.run(loop,looptime,matchdb,pretty)


@device.command()
@click.option("--type",default="board",type=click.Choice(["board","jtag","usbtoserial"]),help="type of device [board,jtag,usbtoserial]")
def supported(type):
    for k,v in _dsc.device_cls.items():
        if v["type"]==type:
            echo(json.dumps({
                "target":v["target"],
                "path":v["path"]
            }))


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
    # open register.vm
    reg = fs.get_json(fs.path(tgt.path,"register.vm"))
    # burn register.vm
    info("Starting device registration")
    tgt.burn(bytearray(base64.standard_b64decode(reg["bin"])))
    if tgt.has_alter_ego:
        # virtualizable device is not the same as uplinkable device -_-
        # algo: find differences between devs 
        pass
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
    if pos>=0 and cnt[pos]>3:
        info("Found chipid:",lines[pos])
    else:
        fatal("Can't find chipid")
    # read chipid
    # call api to register device
    # ### TODO mactchdb true and parse board infomations
    # dev_list = _dsc.run_one(matchdb=False)
    # if uid in dev_list:
    #     #print(dev_list[uid])
    #     ### TODO load basic firmware and parse device informations (on_chip_id, type, etc.)
    #     dinfo = {
    #         "name": name,
    #         "on_chip_id": "123456789",
    #         "type": "flipnclick_sam3x",
    #         "category": "AT91SAM3X8E"
    #     }
    #     headers = {"Authorization": "Bearer "+env.token}
    #     try:
    #         res = zpost(url=dev_url, headers=headers, data=dinfo)
    #         #print(res.json())
    #         if res.json()["status"] == "success":
    #             info("Device",name,"created with uid:", res.json()["data"]["uid"])
    #             ### TODO save mongodb uid in sqlite db
    #         else:
    #             error("Error in device data:", res.json()["message"])
    #     except Exception as e:
    #         error("Can't create device entity")
    #         

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
    vms=tools.get_vms()
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
def open(alias):
    tgt = _dsc.search_for_device(alias)
    if not tgt:
        fatal("Can't find device",alias)
    elif isinstance(tgt,list):
        fatal("Ambiguous alias",[x.alias for x in tgt])

    conn = ConnectionInfo()
    conn.set_serial(tgt.port,**tgt.connection)
    ch = Channel(conn)

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
def alias_put(uid,alias,name,target,chipid):
    if not re.match("^[A-Za-z0-9_:-]{4,}$",alias):
        fatal("Malformed alias")
    devs = _dsc.run_one(True)
    print(devs)
    uids=_dsc.matching_uids(devs, uid)
    print(uids)
    if len(uids)<=0:
        fatal("No devices with uid",uid)
    else:
        uid = uids[0]
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
            "chipid":chipid
        }
        env.put_dev(deventry) 
        #TODO open devdb, get/set uid+unique_alias+name+shortname(this disambiguate a device)


@alias.command("del")
@click.argument("uid")
@click.argument("alias")
@click.option("--name",default=False)
@click.option("--shortname",default=False)
def alias_del(uid,alias,name,shortname):
    pass
