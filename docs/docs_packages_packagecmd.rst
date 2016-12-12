.. module:: Packages

********
Packages
********

The Zerynth Package is extra plug-in of the Zerynth Backend composed by a file or a group of files 
encasing several specific tested features that customers can add to their projects installing it on their pc.

Each z-package is published in a domain related to a namespace directly linked to owner user in order to 
permit that every package has an unique and unambiguous path.

There are several types of Zerynth Packages; here a brief description:

* **core**: principal z-packages on which are based all the Zerynth Tools (Zerynth Studio, Zerynth Toolchain, Standard Library)
* **sys**: z-packages to add system tool platform dependent (Windows, Linux, Mac)
* **board**: z-packages to add new devices to the Zerynth Tools
* **vhal**: z-packages for virtual hardware abstract layer to add low level drivers grouped for microcontroller families
* **lib**: z-packages to add specific class and features to improve new features the z-devices
* **meta**: z-packages that contains list of other z-packages to be installed

Package Commands
================

This module contains all Zerynth Toolchain Commands for interacting with Zerynth Package Entities.
With this commands the Zerynth Users can install new available packages in their installation or can publish a new one 
using the command-line interface terminal.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Packages are:

* info_: to display a Zerynth Package informations
* install_: to install one or more Zerynth Packages
* search__: to search Zerynth Packages according to keywords passed as text query
* publish_: to publisha new Zerynth Package
* update_all_: to update to the last version all Zerynth Packages already installed
* sync_: to sync all z-user local repository database
* published_: to display the list of published z-packages 
* installed_: to display the list of installed z-packages
* updated_: to display the list of updated z-packages
    
.. _info: 
    
Display Package Info
--------------------


This command is used to display informations for specific Zerynth Package passed as argument from the command line running: ::

    Syntax:   ./ztc package info fullname
    Example:  ./ztc package info pack_type.namespace.pack_name

This command take as input the following argument:
    * **fullname** (str) --> the fullname of the z-package (**required**) 

**Errors**:
    * Missing required data
    * Receiving Zerynth Backend response errors

.. note::   The fullname of a z-package is composed by the package type, the package namespace and the package name separated by a dot.
            
    
.. _install:

Install a Package
-----------------

This command is used to install one or more Zerynth Packages on proper installation from the command line running: ::

    Syntax:   ./ztc package install -p --db --last --force --simulate --justnew --offline --mute
    Example:  ./ztc package install -p pack1_type.namespace1.pack1_name -p pack2_type.namespace2.pack_name2 

This command take as input the following arguments:
    * **p** (array) --> list of packages in format fullname:version to be installed (**optional**, default=[]) 
    * **db** (bool) --> flag for not updating local z-package database (**optional**, default=True)
    * **last** (bool) --> flag for installing z-package last version (**optional**, default=False) 
    * **force** (bool) --> flag for forcing installation of z-packages (**optional**, default=False) 
    * **simulate** (bool) --> flag for simulating package installation and display the Zerynth Package Manager operation results (**optional**, default=False) 
    * **justnew** (bool) --> flag for installing only new z-packages against the already installed packages (**optional**, default=False) 
    * **offline** (str) --> the path of the package for the offline installation (**optional**, default=False) 
    * **mute** (bool) --> flag for no diplay log message output (**optional**, default=False) 

**Errors**:
    * Missing required data
    * Conflicts in Package Dependencies
    * Zerynth Package Manager error messages
    * Receiving Zerynth Backend response errors

    
__ search_pack_

.. _search_pack:

Search Packages
---------------

This command is used to search Zerynth Packages on Zerynth Database from the command line with the following syntax: ::

    Syntax:   ./ztc package search query --types
    Example:  ./ztc package search "key1 && (key2 || key3)" --types "lib,board"  

This command take as input the following arguments:
    * **query** (str) --> text query allowing logic operations between keyword (**required**) 
    * **types** (str) --> Comma separated list of package types: lib, sys, board, vhal, core, meta (**optional**, default=“lib")
    
**Errors**:
    * Missing required data
    * Receiving Zerynth Backend response errors

    
.. _publish:

Publish a Package
-----------------

This command is used to publish a owned Zerynth Project transforming it in a new Zerynth Package.
Before publish a z-packages, the Zerynth Users must create their onw namespace to assiciate the related z-package.
The Zerynth Users can publish only "library" type z-packages running from the command line: ::

    Syntax:   ./ztc package publish path version
    Example:  ./ztc package publish ~/my/proj/folder "r1.0.0"  

This command take as input the following arguments:
    * **path** (str) --> path of the z-project to be published (**required**) 
    * **version** (str) --> version of the published package (**required**)
    
**Errors**:
    * Missing required data
    * Missing package.json file with related required fields
    * Missing z-project or git repository associated
    * Receiving Zerynth Backend response errors

.. note:: For publishing a new package is needed a :file:`package.json` file inside
          the passed path argument containing a dictionary with the following required fields: ::
            
            {
                "name":"Z-Package Name",
                "description": "Z-Package Description",
                "fullname": "Z-Package Fullname,
                "keywords":[
                    "key1",
                    "key2",
                    "...",
                ]
                "dependencies":{
                    "dep_pack1": "vers_dep_pack1",
                    "dep_pack2": "vers_dep_pack2",
                    "...": "...",
                },
                "whatsnew":{
                    "description": "What's new description",
                },
                "repo": [
                    "official/community",
                    "...",
                ]
            }

    
.. _update_all:

Update all Packages
-------------------

This command is used to update all the Zerynth Packages installed on the z-user pc from the command line running: ::

    Syntax:   ./ztc package update_all --db --simulate
    Example:  ./ztc package update_all   

This command take as input the following arguments:
    * **db** (bool) -->  flag for not updating local z-package database (**optional**, default=True) 
    * **simulate** (bool) --> flag for simulating the update of all installed packages and display the Zerynth Package Manager operation results (**optional**, default=False)
    
**Errors**:
    * Conflicts in Package Dependencies
    * Zerynth Package Manager error messages
    * Receiving Zerynth Backend response errors

    
.. _sync:

Syncronize all Local Repositories
---------------------------------

This command is used to sync all the Local Repository Database with the Zerynth Remote Repository Database accessible for the related z-user from the command line running: ::

    Syntax:   ./ztc package sync
    Example:  ./ztc package sync   

This command take no argument as input:
    
**Errors**:
    * Receiving Zerynth Backend response errors

.. note:: The Syncronization of local repositories is automatically executed in the "install","update_all" and "updated" commands without the ``--db`` flag.

    
.. _published:

List of Published Packages
--------------------------

This command is used to list all proper Published Zerynth Packages from the command line running: ::

    Syntax:   ./ztc package published --from
    Example:  ./ztc package published   

This command take as input the following argument:
    * **from** (int) --> number from which list the published z-packages (**optional**, default=0) 
    
**Errors**:
    * Receiving Zerynth Backend response errors

    
.. _installed:

List of Installed Packages
--------------------------

This command is used to list all the already Installed Zerynth Packages from the command line running: ::

    Syntax:   ./ztc package installed --extended
    Example:  ./ztc package installed   

This command take as input the following argument:
    * **extended** (bool) --> flag for output full package info (**optional**, default=False) 

    
.. _updated:

List of Updated Packages
------------------------

This command is used to list all Zerynth Packages that are updated against all those installed on the z-user pc from the command line running: ::

    Syntax:   ./ztc package updated --db
    Example:  ./ztc package updated 

This command take as input the following argument:
    * **db** (bool) -->  flag for not updating local z-package database (**optional**, default=True) 
    
**Errors**:
    * Receiving Zerynth Backend response errors

    
