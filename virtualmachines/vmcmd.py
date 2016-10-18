from base import *
import click
import datetime
import json
import sys

vm_url = "http://localhost/zbackend/virtualmachines/"

@cli.group()
def vm():
    pass

@vm.command()
@click.argument("name")
@click.argument("dev")
@click.argument("version")
@click.argument("rtos")
@click.option("--features",default=[])
@click.option("--description",default="[VirtualMachine description goes here]")
def create(name,dev,version,rtos,features,description):
    vminfo = {
        "name":name,
        "dev_uid":dev,
        "description":description,
        "version": version,
        "rtos": rtos,
        "features": features
        }
    info("Creating requested virtual machine...")
    headers = {"Authorization": "Bearer "+env.token}
    try:
        res = zpost(url=vm_url, headers=headers, data=vminfo)
        if res.json()["status"] == "success":
            vminfo.update({"uid": res.json()["data"]["uid"]})
            info("Vitual Machine",name,"created with uid:", res.json()["data"]["uid"])
            fs.makedirs(fs.path(env.vms, vminfo["uid"]))
            fs.set_json(vminfo,fs.path(fs.path(env.vms, vminfo["uid"]),".zvm"))
            try:
                res = zget(url=vm_url+vminfo["uid"], headers=headers)
                if res.status_code == 200:
                    fs.write_file(res.text, fs.path(fs.path(env.vms, vminfo["uid"]),"zerynth.vm"))
                    info("Downloaded Vitual Machine in", fs.path(fs.path(env.vms, vminfo["uid"]),"zerynth.vm"))
                else:
                    warning("Can't download virtual machine:", res.text)
            except Exception as e:
                error("Can't download virtual machine", e)
        else:
            error("Error in creating vm:", res.json()["message"])
    except Exception as e:
        fatal("Can't create vm", e)