import sys
import os
sys.path = [os.path.dirname(os.path.realpath(__file__))]+sys.path

import click
from base import *
import compiler
import devices
import uplinker
import projects
import packages
import virtualmachines
import user
import linter

import json



@cli.command("info")
@click.option("--tools","__tools",flag_value=True, default=False,help="show installed tools")
@click.option("--version","__version",flag_value=True, default=False,help="show current version")
@click.option("--modules","__modules",flag_value=True, default=False,help="show list of installed modules")
@click.option("--devices","__devices",flag_value=True, default=False,help="show installed devices")
@click.option("--vms","__vms",help="show installed virtual machines (target must be specified)")
@click.option("--examples","__examples",flag_value=True, default=False,help="show installed examples")
@click.option("--json","__json",flag_value=True, default=False,help="output info in json format")
@click.option("--pretty","pretty",flag_value=True, default=False,help="output info in readable format")
def __info(__tools,__devices,__vms,__examples,__json,__version,__modules,pretty):
    indent = 4 if pretty else None
    if __tools:
        if __json:
            log(json.dumps(tools.tools,indent=indent))
        else:
            for k,v in tools.tools.items():
                if isinstance(v,str):
                    log(k,"=>",v)
                else:
                    for kk,vv in v.items():
                        log(k+"."+kk,"=>",vv)
    if __devices:
        for dev in tools.get_devices():
            log(json.dumps(dev,indent=indent))
    if __vms:
        if ":" in __vms:
            __vms,chipid = __vms.split(":")
        else:
            chipid = None
        vms = tools.get_vms(__vms,chipid)
        vmdb = {
        }
        for uid,vmf in vms.items():
            vm = fs.get_json(vmf)
            target = vm["dev_type"]
            if target not in vmdb:
                vmdb[target]={}
            if vm["on_chip_id"] not in vmdb[target]:
                vmdb[target][vm["on_chip_id"]]=[]

            vmdb[target][vm["on_chip_id"]].append({
                "file": vmf,
                "target":target,
                "uuid":uid,
                "version":vm["version"],
                "features": [x for x in vm["features"] if not x.startswith("RTOS=")],
                "hash_features": vm["hash_features"],
                "chipid":vm["on_chip_id"],
                "name":vm["name"],
                "desc":vm.get("desc",""),
                "rtos":vm["rtos"]
            })
        log(json.dumps(vmdb,indent=indent))
    if __examples:
        log(json.dumps(tools.get_examples(),indent=indent))

    if __version:
        log(env.var.version)

    if __modules:
        log(json.dumps(tools.get_modules(),indent=indent))

if __name__=="__main__":
    init_all()
    cli()
