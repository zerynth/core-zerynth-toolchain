.. module:: Compiler


Compiler
========

The Zerynth Compiler permits to compile every z-project built with Zerynth.
Every compilation needs a valid z-project path and a valid z-device target to built the related bytecode.

Once compiled a z-project, the z-user could uplink the related bytecode on proper device previous indicated as target.

Compile Command
---------------

In the Compile Command is present a ``--help`` option to show to the users a brief description of the related command and its syntax including arguments and option informations.

The command return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
This command is used to compile a Zerynth Project from the command line running: ::

    Syntax:   ./ztc compile project target --output --include --define
    Example:  ./ztc compile ~/my/proj/folder mikroe_quail

This command take as input the following arguments:
    * **project** (str) --> the path of the Zerynth Project (**required**)
    * **target** (str) --> the target device for the compilation (**required**)
    * **output** (str) --> the path for the output bytecode (**optional**, default=False)
    * **include** (array, multivalue) --> the extra files to be included in compilation phase (**optional**, default=[])
    * **define** (array, multivalue) --> the extra macro to be passed to the low level c-compiler (**optional**, default=[]) 

**Errors**:
    * Missing required data
    * Passing Bad Data
    * Compilation Errors
