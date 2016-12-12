.. module:: Devices

*******
Devices
*******

A Zerynth Device corresponds to a physical electronic board, enabled by Zerynth, that a customer can connect and schedule with the Zerynth Tools.

To run proper applications developed by Zerynth, the z-users must virtualize the board with a dedicated Zerynth Virtual Machine and uplink their application codes.

To know the z-devices enabled by Zerynth Team, here the list of `supported boards`_.

Device Commands
===============

This module contains all Zerynth Toolchain Commands for managing Zerynth Device Entities.
With this commands the Zerynth Users can register and virtualize their boards using the command-line interface terminal.

Before using a z-device, the z-users must assign to it an unique alias name creating a local database device entity.
This operation will permit to the z-users to refer to their boards for executing commands on them and 
will permit to the Zerynth Tool to auto-recognize the boards every time z-users connect to them to their pc.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Devices are:

* `alias put`_: to create a new local database device entity assigning an unique alias name
* `alias del`_: to delete a z-device referred to a specific alias name
* discover_: to discover the connected z-devices
* supported_: to list supported z-devices
* register_: to register new z-devices
* virtualize_: to virtualize a z-devices
* open_: to open serial port for the communication with the z-device

    
.. _alias_put:

Alias Put
---------

This command is used to create a new local database device entity with a custom unique alias name from the command line with this syntax: ::

    Syntax:   ./ztc device alias put uid alias target --name --chipid --remote_id --classname
    Example:  ./ztc device alias put 776ff4bc8fdfd700ef92005c7024b3af914b86e6 uid_alias_name --name "myBoard"

This command take as input the following arguments:
    * **uid** (str) -->  the uid of the related device found in the `discover` command diplay results (**required**)
    * **alias** (str) --> the unique alias name to assign to the device (**required**)
    * **target** (str) -->  the target of the z-device (**required**)
    * **name** (str) --> the name of the z-device (**optional**, default=False)
    * **classname** (str) --> the classname of the z-device (**optional**, default="")


**Errors**:
    * Missing input required data
    * Errors on matching device target or classname (for multiclass devices) 

    
.. _alias_del:

Alias Del
---------

This command is used to delete a z-device from the local database running this command from the terminal: ::

    Syntax:   ./ztc project alias del alias
    Example:  ./ztc project alias del uid_alias_name

This command take as input the following arguments:
    * **alias** (str) --> the unique alias name to assign to the device (**required**)
    
**Errors**:
    * Missing input required data
    * Wrong Alias

    
.. _discover:

Discover Devices
----------------

This command is used to discover devices connected to the z-user pc using the command line with this syntax: ::

    Syntax:   ./ztc device discover --loop --looptime --matchdb
    Example:  ./ztc device discover --matchdb

This command take as input the following arguments:
    * **loop** (bool) --> flag to exec in infinite loop this command (**optional**, default=False)
    * **looptime** (int) --> time to sleep at the end of the loop operations (**optional**, default=2)
    * **matchdb** (bool) --> flag to enable the matching between devices connected and z-device in local database (**optional**; default=False)

    
.. _supported:

List of Supported Devices
-------------------------

This command is used to list supported devices from the command line with this syntax: ::

    Syntax:   ./ztc device supported --type
    Example:  ./ztc device supported --type board

This command take as input the following argument:
    * **type** (str) --> type of the device (**optional**, default=“board")

.. note:: the type of devices available are: "board", "jtag", and "usbtoserial"

    
.. _register:

Register a Device
-----------------

This command is used to register a new Zerynth Device on the Zerynth Backend Database from the command line with this syntax: ::

    Syntax:   ./ztc device register alias
    Example:  ./ztc device register uid_alias_name

This command take as input the following argument:
    * **alias** (str) --> the alias od the z-device (**required**)

**Errors**:
    * Missing input required data
    * Wrong Alias
    * Receiving Zerynth Backend response errors

.. note:: This operation is needed before first virtualization of a z-device;  

    
.. _virtualize:

Virtualize a Device
-------------------

This command is used to virtualize a Zerynth Device installing on the board the real time operative system to
abilitate for running customer application code. the ``virtualize`` command has this syntax: ::

    Syntax:   ./ztc device virtualize alias vmuid
    Example:  ./ztc device virtualize uid_alias_name 3Ss_HOgpQGW7oKtYmNESPQ

This command take as input the following arguments:
    * **alias** (str) --> the alias of the z-device (**required**)
    * **vmuid** (str) --> the uid of the Zerynth Virtual Machine to load on the z-device(**required**)

**Errors**:
    * Missing required data
    * Wrong Alias
    * Wrong uid for the virtual machine

.. note:: Before virtualizing a z-device, is needed to :ref:`create<Create a Virtual Machine>` a Zerynth Virtual Machine for that specific z-device

    
.. _open:

Open a Serial Port
------------------

This command is used to open a serial port to communicate with the z-device from the command line with this syntax: ::

    Syntax:   ./ztc device open alias --echo
    Example:  ./ztc device open uid_alias_name --echo

This command take as input the following arguments:
    * **alias** (str) --> the alias name of the z-device (**required**)
    * **echo** (str) --> flag for printing typed characters to stdin (**optional**, default=False)

**Errors**:
    * Missing required data
    * Wrong Alias
    
