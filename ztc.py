import click
from base import *
import compiler
import devices
import uplinker
import projects
import packages
import virtualmachines
import namespaces

import json


@cli.command("info")
@click.option("--tools","__tools",flag_value=True, default=False,help="show installed tools")
@click.option("--devices","__devices",flag_value=True, default=False,help="show installed devices")
@click.option("--packages","__packages",flag_value=True, default=False,help="show installed packages")
@click.option("--vms","__vms",flag_value=True, default=False,help="show installed virtual machines")
@click.option("--json","__json",flag_value=True, default=False,help="output info in json format")
@click.option("--pretty","pretty",flag_value=True, default=False,help="output info in readable format")
def __info(__tools,__devices,__packages,__vms,__json,pretty):
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
        info("DEVICES")
    if __packages:
        info("PACKAGES")
    if __vms:
        vms = tools.get_vms()
        vmdb = {
        }
        for uid,vmf in vms.items():
            vm = fs.get_json(vmf)
            target = vm["board"]
            if target not in vmdb:
                vmdb[target]={}
            vmdb[target][vm["version"]]={
                "file": vmf,
                "target":target,
                "uuid":uid,
                "version":vm["version"],
                "props":[], #TODO: add props
                "props_hash":"---", #TODO: add hash
                "chipid":"", #TODO: add chipid
                "name":vm["name"],
                "desc":vm["desc"]
            }
        log(json.dumps(vmdb,indent=indent))



if __name__=="__main__":
    init_all()
    cli()
