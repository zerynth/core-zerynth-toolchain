from base import *
from .discover import *
import click
import re

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


def _target_exists(target):
    if not target: return False
    for k,v in _dsc.device_cls.items():
        if "target" in v and v["target"]==target:
            return True
    return False

@device.command()
@click.argument("uid")
@click.argument("name")
def register(uid, name):
    ### TODO mactchdb true and parse board infomations
    dev_list = _dsc.run_one(matchdb=False)
    if uid in dev_list:
        #print(dev_list[uid])
        ### TODO load basic firmware and parse device informations (on_chip_id, type, etc.)
        dinfo = {
            "name": name,
            "on_chip_id": "123456789",
            "type": "flipnclick_sam3x",
            "category": "AT91SAM3X8E"
        }
        headers = {"Authorization": "Bearer "+env.token}
        try:
            res = zpost(url=dev_url, headers=headers, data=dinfo)
            #print(res.json())
            if res.json()["status"] == "success":
                info("Device",name,"created with uid:", res.json()["data"]["uid"])
                ### TODO save mongodb uid in sqlite db
            else:
                error("Error in device data:", res.json()["message"])
        except Exception as e:
            error("Can't create device entity")





##### DEVICE ALIAS [PUT|DEL]

@device.group()
def alias():
    pass


#TODO test once boards are ok
@alias.command("put")
@click.argument("uid")
@click.argument("alias")
@click.option("--name",default=False)
@click.option("--target",default=False)
def alias_put(uid,alias,name,target):
    if not re.match("^[A-Za-z0-9_-]{4,}$",alias):
        fatal("Malformed alias")
    devs = _dsc.run_one(True)
    print(devs)
    uids=_dsc.matching_uids(devs, uid)
    print(uids)
    if len(uids)<=0:
        fatal("No devices with uid",uid)
    elif len(uids)==1:
        uid = uids[0]
        aliaskey = alias
        aliases = env.get_dev(uid)
        aliasuid = aliases[alias].uid if alias in aliases else None
        deventry = {
            "alias":alias,
            "uid":uid,
            "name": aliases[alias].name if not name and aliasuid!=None else "",
            "target": aliases[alias].target if not target and aliasuid!=None else "",
        }
        if target and not _target_exists(target):
                fatal("No such target",target)
        env.put_dev(deventry)
        print("lllll")
        #TODO open devdb, get/set uid+unique_alias+name+shortname(this disambiguate a device)
    else:
        fatal("Ambiguous uid:",uids)


@alias.command("del")
@click.argument("uid")
@click.argument("alias")
@click.option("--name",default=False)
@click.option("--shortname",default=False)
def alias_del(uid,alias,name,shortname):
    pass
