from base import *
import click
import datetime
import json
import sys


def download_vm(uid,version):
    res = zget(url=env.api.vm+"/"+uid+"/"+version)
    rj = res.json()
    if rj["status"]=="success":
        vmpath = fs.path(env.vms, rj["data"]["dev_type"],rj["data"]["dev_uid"])
        fs.makedirs(vmpath)
        fs.set_json(rj["data"], fs.path(vmpath,uid+"_"+version+"_"+rj["data"]["hash_features"]+"_"+rj["data"]["rtos"]+".vm"))
        info("Downloaded Vitual Machine in", vmpath,"with uid",uid)
    else:
        error("Can't download virtual machine:", rj["message"])


@cli.group()
def vm():
    pass

@vm.command()
@click.argument("device")
@click.argument("version")
@click.argument("rtos")
@click.option("-feat", multiple=True, type=str)
@click.option("--name", default="")
def create(device,version,rtos,feat,name):
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
            error("Error while creating vm:", rj["message"])
    except TimeoutException as e:
        critical("No answer yet")
    except Exception as e:
        critical("Can't create vm", exc=e)


@vm.command()
@click.argument("uid")
@click.argument("version")
def download(uid,version):
    try:
        download_vm(uid,version)
    except Exception as e:
        critical("Can't download vm", exc=e)


@vm.command("list")
@click.option("--from","_from",default=0)
@click.option("--pretty","pretty",flag_value=True, default=False,help="output info in readable format")
@click.option("--core_dep",default=None)
def __list(_from,pretty,core_dep):
    indent = 4 if pretty else None
    try:
        prms = {"from":_from}
        if core_dep: prms["core_dep"]=core_dep
        res = zget(url=env.api.vm,params=prms)
        rj = res.json()
        if rj["status"]=="success":
            log(json.dumps(rj["data"],indent=indent))
        else:
            error("Can't get vm list",rj["message"])
    except Exception as e:
        critical("Can't get vm list",exc=e)

