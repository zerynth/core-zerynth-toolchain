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

    
