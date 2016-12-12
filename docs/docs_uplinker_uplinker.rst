.. module:: Uplinker


Uplinker
========

The Zerynth Uplinker permits to load every compiled z-project on the related device.
Every uplink operation needs a valid built bytecode path and a valid, already virtualized, z-device uid to migrate the firmware on the board.

Once upliked the bytecode, the z-device will be able to run the application developed.

Uplink Command
---------------

In the Uplink Command is present a ``--help`` option to show to the users a brief description of the related command and its syntax including arguments and option informations.

The command return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
This command is used to uplink a Zerynth Project compiled in bytecode on a device from the command line running: ::

    Syntax:   ./ztc uplink uid bytecode --loop
    Example:  ./ztc uplink ntaWYcCqSLGB1QtBLXY__w ~/my/bytecode/folder 

This command take as input the following arguments:
    * **uid** (str) --> the uid of the z-device on which to load the bytecode (**required**)
    * **bytecode** (str) --> the path of the bytecode file (**required**)
    * **loop** (int) --> the number of attemps to try to load the bytecode on the device (**optional**, default=5)
    
**Errors**:
    * Missing required data
    * Passing Bad Data
    * Uplink Operation Errors
