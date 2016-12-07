"""
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

"""
from base import *
from .compiler import Compiler
from .exceptions import *
import click

@cli.command(help="Compile a Zerynth Project. \n\n Arguments: \n\n PROJECT: Path of the z-project. \n\n TARGET: target device for the compilation.")
@click.argument("project",type=click.Path())
@click.argument("target")
@click.option("--output","-o",default=False,help="Path for output file")
@click.option("--include","-I",default=[],multiple=True,help="Path for including extra source files ((multi-value option)")
@click.option("--define","-D",default=[],multiple=True,help="Defined macro to be passed to low level c-compiler (multi-value option")
def compile(project,target,output,include,define):
    try:
        prj = fs.get_json(fs.path(project,".zproject"))
    except:
        fatal("Can't open project at",project)
    #TODO: check target is valid
    mainfile = fs.path(project,"main.py")
    compiler = Compiler(mainfile,target,include,define)
    try:
        binary, reprs = compiler.compile()
    except CModuleNotFound as e:
        fatal("Can't find module","["+e.module+"]","imported by","["+e.filename+"]","at line",e.line)
    except CNativeNotFound as e:
        fatal("Can't find native","["+e.errmsg+"]","in","["+e.filename+"]","at line",e.line)
    except CUnknownNative as e:
        fatal("Can't find C native","["+e.native_message+"]","in","["+e.filename+"]","at line",e.line)
    except CNativeError as e:
        fatal("Error in C natives","["+e.errmsg+"]","in","["+e.filename+"]","at line",e.line)
    except CNameError as e:
        fatal("Can't find name","["+e.name+"]","in","["+e.filename+"]","at line",e.line)
    except CNameConstantError as e:
        fatal("Unknown","[constant]","in","["+e.filename+"]","at line",e.line)
    except CSyntaxError as e:
        fatal("Syntax error","["+e.errmsg+"]","in","["+e.filename+"]","at line",e.line)
    except CWrongSyntax as e:
        fatal("Syntax error","["+e.errmsg+"]","in","["+e.filename+"]","at line",e.line)
    except CUnsupportedFeatureError as e:
        fatal("Unsupported feature","["+e.feature+"]","in","["+e.filename+"]","at line",e.line)
    except Exception as e:
        critical("Unexpected exception",exc=e)
    if not output:
        output=fs.basename(project)+".vbo"
    elif not output.endswith(".vbo"):
        output+=".vbo"
    info("Saving to",output)
    binary["repr"]=[rep.toDict() for rep in reprs]
    binary["project"]=project
    fs.set_json(binary,output)
    info("Compilation Ok")





