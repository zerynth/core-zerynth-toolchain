.. _ztc-cmd-package:

********
Packages
********

The ZTC features a package manager to search, install and publish components of the Zerynth ecosystem.
A package is an archive generated from a tagged git repository and identified by a unique :samp:`fullname`.
There exist several package types, each one targeting a different Zerynth functionality:

* :samp:`core` packages contain core Zerynth components (i.e. the ZTC, the Studio, etc...)
* :samp:`sys` packages contain plaform dependent third party tools used by the ZTC (i.e. gcc, device specific tools, the Python runtime, etc..)
* :samp:`board` packages contain device definitions
* :samp:`vhal` packages contain low level drivers for various microcontroller families
* :samp:`meta` packages contain sets of other packages
* :samp:`lib` packages contain Zerynth libraries to add new modules to Zerynth programs

A package :samp:`fullname` is composed of three fields uniquely identifying the package:

* type
* :ref:`namespace <ztc-cmd-namespace>`
* package name

For example, the package :samp:`lib.broadcom.bmc43362` contains the Python driver for the Broadcom bcm43362 wifi chip. 
Its fullname contains the type (:samp:`lib`), the namespace (:samp:`broadcom`) grouping all packages implementing Broadcom drivers, and the actual package name (:samp:`bcm43362`) specifying which particular driver is implemented.
A package has one or more available versions each one tagged following a modified `semantic versionig <http://semver.org>`_ scheme.

Moreover packages can belong to multiple "repositories" (collections of packages). There are two main public repositories, the :samp:`official` one, containing packages created, published and mantained by the Zerynth team, and the :samp:`community` one, containing packages created by community members.

The ZTC mantains a local databases of installed packages and refers to the online database of packages to check for updates and new packages.

    
.. _ztc-cmd-package-info: 
    
Package Info
------------

The command: ::

    ztc package info fullname

displays information about the package identified by :samp:`fullname`.
            
    
.. _ztc-cmd-package-install:

Install
-------

Packages can be added to the current Zerynth installation with the command: ::

    ztc package install -p fullname:version

where :samp:`fullname` is the package fullname and :samp:`version` is the version of the package to install (or update if a previous version is already installed).
The command first downloads the online package database and then recursively check package dependencies in order to install all required packages.

The command accepts many additional options:

* :option:`-p fullname:version` can be repeated multiple times to install more than one package at a time
* :option:`--db` skips the downloading of the online package database
* :option:`--last` while checking dependencies, selects the more up to date version of the dependency
* :option:`--force` performs installation of packages ignoring dependencies errors (warning: this could break the ZTC, use with caution)
* :option:`--justnew` while checking dependencies, avoids installing packages whose version is already installed
* :option:`--simulate` performs a simulated install, printing the list of modified packages only
* :option:`--offline path` performs installation searching packages in :samp:`path` instead of downloading them. Used for offline installations.
* :option:`--mute` supresses messages to stdout


.. note:: when the package :samp:`meta.zerynth.core` is installed, a new ZTC version is created and will be automatically used on subsequent executions of the ZTC. Previously installed versions of the ZTC can be reactivated by modifying the :file:`config.json` setting the :samp:`version` field to the desired value. 

.. note:: packages :samp:`sys.zerynth.runtime` and :samp:`sys.zerynt.browser` are not automatically installed! They are downloaded and uncompressed under :file:`sys/newpython` and :file:`sys/newbrowser` directories respectively. For the packages to be activated, such directories must be renamed to :file:`sys/python` and :file:`sys/browser` respectively.

    
.. _ztc-cmd-package-search:

Search
------

To search the online package database issue the command: ::

    ztc package search query

where :samp:`query` is a string composed of terms separated by spaces and optionally by logical operators. Allowed operators are :samp:`&&` for AND and :samp:`||` for OR. Round parentesis can also used.

The terms provided in the :samp:`query` are searched in the following attributes of a package:

* title
* description
* fullname
* list of package keywords

The command accepts the option :option:`--types typelist` where :samp:`typelist` is a comma separated list of package types to be searched. By default, the search is performed on :samp:`lib` packages only and only the first 50 results ordered by relevance are returned.


    
.. _ztc-cmd-package-publish:

Publishing a package
--------------------

Zerynth projects can be published as library packages and publicly shared on different repositories (default is :samp:`community`). In order to convert a project into a publishable packages some requirements must be met:

* The project must exist as a repository on the Zerynth backend (see :ref:`git_init <ztc-cmd-project-git_init>`)
* The user must own at least a :ref:`namespace <ztc-cmd-namespace-create>`
* The project folder must contain a :file:`package.json` file with all relevant package information

In particular, the :file:`package.json` must contain the following mandatory fields:

* :samp:`title`: the title of the package
* :samp:`description`: a longer description of the package
* :samp:`keywords`: an array of keywords that will be used by the package search engine
* :samp:`repo`: the name of the repository to publish to. Users can generally publish only to "community" unless permission is granted for a different repository
* :samp:`fullname`: the unique name of the package obtained from its type (generally :samp:`lib`), a namespace owned or accessible by the user and the actual library name.
* :samp:`whatsnew`: a string describing what has changed from the previous version of the package
* :samp:`dependencies`: a dictionary containing the required packages that must be installed together with the package. A dictionary key is the fullnames of a required package whereas the value is the minimum required version of such package.

An example of :file:`package.json`: ::

    {
        "fullname": "lib.foo.ds1307",
        "title": "DS1307 Real Time Clock",
        "description": "Foo's DS1307 RTC Driver ... ",
        "keywords": [
            "rtc",
            "maxim",
            "time"
        ],
        "repo": "community",
        "whatsnew": "Fixed I2C bugs",
        "dependencies": {
            "core.zerynth.stdlib":"r2.0.0"
        }
        
    }

The previous file describes the package :samp:`lib.foo.ds1307`, published in the :samp:`community` repository under the namespace :samp:`foo`. It is a package for DS1307 RTC that requires the Zerynth standard library to be installed with a version greater or equal then :samp:`r2.0.0`.

The command: ::

    ztc package publish path version

first checks for the validity of the :file:`package.json` at :samp:`path`, then modifies it adding the specified :samp:`version` and the remote git repository url. A git commit of the project is created and tagged with the :samp:`version` parameter; the commit is pushed to the Zerynth backend together with the just created tag. The backend is informed of the new package version and queues it for review. After the review process is finished, the package version will be available for installation.

Package Documentation
^^^^^^^^^^^^^^^^^^^^^

Each published package can feature its own documentation that will be built and hosted on the Zerynth documentation website. The documentation files must be saved under a :file:`docs` folder in the project and formatted as reported :ref:`here <ztc-cmd-project-make_doc>`. It is strongly suggested to build the documentation locally and double check for typos or reStructuredText errors.


Package Examples
^^^^^^^^^^^^^^^^

Packages be distributed with a set of examples stored under an :file:`examples` folder in the project. Each example must be contained in its own folder respecting the following requirements:

* The example folder name will be converted into the example "title" (shown in the Zerynth Studio example panel) by replacing underscores ("_") with spaces
* The example folder can contain any number of files, but only two are mandatory: :file:`main.py`, the entry point file and :file:`project.md`, a description of the example. Both files will be automatically included in the package documentation.

Moreover, for the examples to be displayed in the Zerynth Studio example panel, a file :file:`order.txt` must be placed in the :file:`examples` folder. It contains information about the example positioning in the example tree: ::

    ; order.txt of the lib.adafruit.neopixel package
    ; comments starts with ";"
    ; inner tree nodes labels start with a number of "#" corresponding to their level
    ; leaves corresponds to the actual example folder name
    #Adafruit
        ##Neopixel
           Neopixel_LED_Strips
           Neopixel_Advanced

    ; this files is translated to:
    ; example root
    ; |
    ; |--- ...
    ; |--- ...
    ; |--- Adafruit
    ; |        |--- ...
    ; |        \--- Neopixel
    ; |                |--- Neopixel LED Strips
    ; |                \--- Neopixel Advanced
    ; |--- ...
    ; |--- ...

    
.. _ztc-cmd-packages-update_all:

Update all packages
-------------------

The current ZTC installation can be updated with the following command: ::

    ztc package update_all

All packages are checked for new versions and installed. If the :samp:`meta.zerynth.core` packages is updated, a new ZTC installation is also created.

Options :option:`--db` and :option:`--simulate` are available with the same meaning as in the :ref:`install <ztc-cmd-package-install>` command.
    
.. _ztc-cmd-package-sync:

Sync
----

The local database of available packages is a copy of the online package database. The command: ::

    ztc package sync

overwrites the local database with the online one. Subsequent ZTC commands on packages will use the updated database.
Most package commands automatically sync package database before executing. Such behaviour can be disabled by providing the :option:`--db` option

    
.. ztc-cmd-package-published:

Published packages
------------------

The command: ::

    ztc package published

retrieves the list of packages published by the user.

    
.. _ztc-cmd-package-installed:

Installed packages
------------------

The list of currently installed packages can be retrieved with: ::

    ztc package installed

providing the :option:`--extended` prints additional information.

    
.. ztc-cmd_package-updated:

Updated packages
----------------

The list of packages with updated versions with respect to the current installation can be retrieved with: ::
    
    ztc package updated

    
.. ztc-cmd_package-available:

Available packages
------------------

The list of packages available on the backend can be retrieved with: ::
    
    ztc package available

    
.. ztc-cmd_package-devices:

New Devices
-----------

The list of new supported devices with respect to the current installation can be retrieved with: ::
    
    ztc package devices

    
