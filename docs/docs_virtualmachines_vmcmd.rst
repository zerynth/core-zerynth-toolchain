.. module:: VMs

****************
Virtual Machines 
****************

The Zerynth Virtual Machine is the Multi-Thread Real Time Operative System that, once installed on the related device enabled by Zerynth,
permits to the users to execute their Zerynth Projects uplinked on their device.

Every Virtual Machine can be created after a device registration and can be compiled for the specific related device
with the real time operative system and features choosen by the users.


Virtual Machine Commands
========================

This module contains all Zerynth Toolchain Commands for managing Zerynth Virtual Machine Entities.
With this commands the Zerynth Users can handle all their virtual machines using the command-line interface terminal.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Virtual Machines are:

* create__: to create a Zerynth Virtual Machine
* download_: to download an already compiled owned Zerynth Virtual Machine
* list__: to list all owned Zerynth Virtual Machines
* available_: to retrieve a specific owned Zerynth Virtual Machine
    
__ create_vm_

.. _create_vm:

Create a Virtual Machine
------------------------

This command is used to create and download a new Zerynth Virtual Machine from the command line with this syntax: ::

    Syntax:   ./ztc vm create device version rtos -feat --name
    Example:  ./ztc vm create myDev 1.0.0 chibi2 --name "myZVM"

This command take as input the following arguments:
    * **device** (str) --> the alias name of the device that the users want to virtualize (**required**)
    * **version** (str) --> the version of the virtual machine (**required**)
    * **rtos** (str) --> the rtos choosen by the users for the virtual machine (**required**)
    * **feat** (str, multivalue) --> the extra features choosen by the users (only pro) for the virtual machine (**optional**, default=“")
    * **name** (str) --> the name of the virtual machine (**optional**, default=“") 

**Errors**:
    * Missing required data
    * User Asset Limit Overflow
    * Bad alias for the Device
    * Rtos unsupported for the device

.. note:: The version argument of this command must following the standard versioning nomenclature.
          Available Versions: "r1.0.0", "r1.0.1"
.. warning:: Extra features not available yet

    
.. _download:

Download a Virtual Machine
--------------------------

This command is used to download an existing Zerynth Virtual Machine from the command line with this syntax: ::

    Syntax:   ./ztc vm download uid version
    Example:  ./ztc vm download 3Ss_HOgpQGW7oKtYmNESPQ r1.0.0

The uid of an already compiled and available virtual machine can be found under .Zerynth/vms folder or
executing the :func:`list` function described in the next section.

This command take as input the following arguments:
    * **uid** (str) --> the uid of the virtual machine (**required**)
    * **version** (str) --> the version of the virtual machine (**required**)

**Errors**:
    * Missing required data
    * Wrong uid for the virtual machine

.. note:: The version argument of this command must following the standard versioning nomenclature.
          Available Versions: "r1.0.0", "r1.0.1"

    
__ list_vm_

.. _list_vm:

List Virtual Machines
---------------------

This command is used to list all proper Zerynth Virtual Machines already compiled from the command line running: ::

    Syntax:   ./ztc vm list --from --core_dep
    Example:  ./ztc vm list --from 0  

This command take as input the following arguments:
    * **from** (int) --> the number from which display the virtual machine list (**optional**, default=0)
    * **core_dep** (str) --> select the virtual machine from availables according to the related core dependency (**optional**, default=None)

**Errors**:
    * Wrong data for the virtual machine list

    
.. _available:

Retrieve a Virtual Machine
--------------------------

This command is used to retrieve a specific Zerynth Virtual Machine informations according to the target argument from the command line with this syntax: ::

    Syntax:   ./ztc vm available target
    Example:  ./ztc vm available particle_photon

This command take as input the following argument:
    * **target** (str) --> target of the virtual machine(**required**)

**Errors**:
    * Wrong data for retriving virtual machine

    
