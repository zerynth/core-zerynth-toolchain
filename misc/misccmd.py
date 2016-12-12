"""

.. _ztc-misc:

Miscellanea
===========

The commands in this section produce information about the ZTC status.

   """

from base import *
import click




@cli.command("info",help="Display info about ZTC status.")
@click.option("--tools","__tools",flag_value=True, default=False,help="Display installed tools")
@click.option("--version","__version",flag_value=True, default=False,help="Display current version")
@click.option("--modules","__modules",flag_value=True, default=False,help="Display installed Zerynth modules")
@click.option("--devices","__devices",flag_value=True, default=False,help="Display supported devices currently installed")
@click.option("--vms","__vms", help="Display installed virtual machines for a specific target")
@click.option("--examples","__examples",flag_value=True, default=False,help="Display the list of installed examples")
def __info(__tools,__devices,__vms,__examples,__version,__modules):
    """ 
Info
----

The :command:`info` command  displays information about the status of the ZTC.

It takes the following options (one at a time):

* :option:`--version` display the current version of the ZTC.
* :option:`--devices` display the list of supported devices currently installed.
* :option:`--tools` display the list of available ZTC tools. A ZTC tool is a third party program used to accomplish a particular task. For example the gcc compiler for various architecture is a ZTC tool.
* :option:`--modules` display the list of installed Zerynth libraries that can be imported in a Zerynth program.
* :option:`--examples` display the list of installed examples gathered from all the installed libraries.
* :option:`--vms target` display the list of virtual machines in the current installation for the specified :samp:`target`

    """
    if __tools:
        if env.human:
            table = []
            for k,v in tools.tools.items():
                if isinstance(v,str):
                    table.append([k,v])
                    log(k,"=>",v)
                else:
                    for kk,vv in v.items():
                        table.append([k+"."+kk,vv])
            log_table(table)
        else:
            log_json(tools.tools)
        return

    if __devices:
        table = []
                
        for dev in tools.get_devices():
            if env.human:
                #TODO: print in human readable format
                table.append([dev["type"],dev.get("target","---"),dev.get("name","---")])
            else:
                log_json(dev)
        if env.human:
            log_table(table,headers=["type","target","name"])
        return
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
        if env.human:
            table = []
            for target,chv in vmdb.items():
                for chipid,nfo in chv.items():
                    for nn in nfo:
                        table.append([target,chipid,nn["uuid"],nn["rtos"],nn["features"],nn["file"]])
            log_table(table,headers=["target","chipid","uid","rtos","features","path"])
        else:
            log_json(vmdb)
        return

    if __examples:
        exl = tools.get_examples()
        if env.human:
            table = []
            for ex in exl:
                table.append([ex["name"],ex["path"],ex["tag"]])
            log_table(table,headers=["title","path","tags"])
        else:
            log_json(exl)
        return

    if __version:
        log(env.var.version)
        return

    if __modules:
        mods = tools.get_modules()
        if env.human:
            table = []
            for mod in sorted(mods):
                table.append([mod,mods[mod]])
            log_table(table,headers=["from","import"])
        else:
            log_json(mods)