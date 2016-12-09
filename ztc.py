"""
.. module:: ZTC

*****************
Zerynth Toolchain
*****************

The Zerynth Toolchain is composed by a set of programming tools that allow the users to manage and interact with all the Zerynth Entities and Functionalities with che Command Line Interface.

This software has been designed to give the possibility to work and develop with Zerynth Tools without GUI.
The Zerynth Toolchain can also be integrated with other or preferred Integrated Development Environments (IDEs) that 
can be customized for using the ZTC Commands.

.. note:: To execute any ZTC Command is needed an active internet connection and the users must be logged in their Zerynth Account


Zerynth ToolChain Commands
==========================

This module contains all Zerynth Toolchain Commands for managing Zerynth Toolchain Entities.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The Zerynth Entities that can be managed by ZTC are:

* :ref:`Users`: to manage proper Zerynth Account and Profile
* :ref:`Projects`: to manage Zerynth Projects
* :ref:`Devices`: to manage Zerynth Devices
* :ref:`Compiler, Uplinker and Linter`: to manage compilation and uplink operations
* :ref:`Virtual Machines`: to manage Zerynth Virtual Machine
* :ref:`Namespaces`: to manage Zerynth Namespaces
* :ref:`Packages`: to manage Zerynth Packages
    """

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



@cli.command("info",help="Display Zerynth Toolchain informations.")
@click.option("--tools","__tools",flag_value=True, default=False,help="Show installed tools.")
@click.option("--version","__version",flag_value=True, default=False,help="Show current version.")
@click.option("--modules","__modules",flag_value=True, default=False,help="Show list of installed modules.")
@click.option("--devices","__devices",flag_value=True, default=False,help="Show installed devices.")
@click.option("--vms","__vms",help="Show installed virtual machines (target must be specified).")
@click.option("--examples","__examples",flag_value=True, default=False,help="Show installed examples.")
def __info(__tools,__devices,__vms,__examples,__version,__modules):
    """ 
Info Command
------------

This command is used to display Zerynth Toolchain System Informations from the command line with this syntax: ::

    Syntax:   ./ztc info --tools --version --modules --devices --vms --examples
    Example:  ./ztc info --devices --vms target

This command take as input the following arguments:
    * **tools** (bool) --> flag to display all installed system tools on current Zerynth installation (**optional**, default=False)
    * **version** (bool) --> flag to display current version of the installed Zerynth Tool (**optional**, default=False)
    * **modules** (bool) --> flag to display all installed modules on current Zerynth installation (**optional**; default=False)
    * **devices** (bool) --> flag to diplay all installed devices in current Zerynth installation (**optional**; default=False)
    * **vms** (str) --> to display all vms installed in the current Zerynth installation (**optional**, target device must be specified)
    * **examples** (bool) --> flag to display all installed example in current Zerynth installation (**optional**, default=False)

.. note:: All ZTC commands have some generic option that can be setted for formatting output, enabling colors, etc.
          Here below the sintax and the complete list of options: ::

              Syntax:   ./ztc -v --colors/--no-colors --traceback/--no-traceback --user_agent -J --pretty "rest of ztc command"
              Example:  ./ztc -J --pretty "rest of ztc command"
            
          * **-v, verbose** (bool) --> flag to display details about the results of running command (**optional**, default=False)
          * **colors/no-colors, nocolors** (bool) --> flag to enable/disable colors in log messages (**optional**, default=True)
          * **traceback/no-traceback** (bool) --> flag to enable/disable exception traceback printing on criticals (**optional**, default=True)
          * **user_agent** (str) --> to insert custom user agent (**optional**, default=“ztc")
          * **J** (bool) --> to display output in json format (**optional**, default=False)
          * **pretty** (bool) --> to display pretty pretty json output (woking only with 'J' flag enabled) (**optional**, default=False)

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
        for dev in tools.get_devices():
            if env.human:
                #TODO: print in human readable format
                log_json(dev)
            else:
                log_json(dev)
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
        log_json(tools.get_examples())

    if __version:
        log(env.var.version)

    if __modules:
        log_json(tools.get_modules())

if __name__=="__main__":
    init_all()
    cli()
