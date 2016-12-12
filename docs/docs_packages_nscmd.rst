.. module:: Namespaces

**********
Namespaces
**********

The Zerynth Namespace is a Database Entity used to organize all the published package owned by a Zerynth User.

Each Namespace is referred to an associated repository domain and includes packages that can be visualized and downloaded by all the other z-users (according to their repositories attributes).

Namespace Commands
==================

This module contains all Zerynth Toolchain Commands for managing Zerynth Namespace Entities.
With this commands the Zerynth Users can handle and monitor all their namespaces using the command-line interface terminal.

In all commands is present a ``--help`` option to show to the users a brief description of the related selected command and its syntax including arguments and option informations.

All commands return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The actions that can be executed on Zerynth Namespaces are:

* create__: to create a Zerynth Namespace
* list__: to list all owned Zerynth Namespaces
    
__ create_ns_

.. _create_ns:

Create a Namespace
------------------

This command is used to create and download a new Zerynth Namespace from the command line with this syntax: ::

    Syntax:   ./ztc namespace create name
    Example:  ./ztc namespace create myNS

This command take as input the following arguments:
    * **name** (str) --> the name of the namespace (**required**)

**Errors**:
    * Missing required data
    * User Asset Limit Overflow
    * Receiving Zerynth Backend response errors

    
__ list_ns_

.. _list_ns:

List Namespaces
---------------

This command is used to list all proper Zerynth Namespaces already compiled from the command line running: ::

    Syntax:   ./ztc namespace list
    Example:  ./ztc namespace list  

This command take no input argument.

**Errors**:
    * Receiving Zerynth Backend response errors

    
