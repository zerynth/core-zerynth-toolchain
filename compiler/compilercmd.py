"""
.. _ztc-cmd-compile:

Compiler
========

The ZTC compiler takes a project as input and produces an executable bytecode file ready to be :ref:`uplinked <ztc-cmd-uplink>` on a :ref:`virtualized <ztc-cmd-device-virtualize>`.

The command: ::
    
        ztc compiler project target

compiles the source files found at :samp:`project` (the project path) for a device with target :samp:`target`.

The entry point of the program is the file :file:`main.py`. Every additional Python module needed wil be searched in the following order:

1. Project directory
2. Directories passed with the :option:`-I` option in the given order (see below)
3. The Zerynth standard library
4. The installed libraries

Since Zerynth programs allow mixed C/Python code, the compiler also scans for C source files and compiles them with the appropriate C compiler for :samp:`target`.
C object files are packed and included in the output bytecode.

The :command:`compile` command accepts additional options:

* :option:`-I/--include path`, adds :samp:`path` to the list of directories scanned for Zerynth modules. This option can be repeated multiple times.
* :option:`-D/--define def`, adds a C macro definition as a parameter for native C compiler. This option can be repeated multiple times.
* :option:`-o/--output path`, specifies the path for the output file. If not specified it is :file:`main.vbo` in the project folder.


"""
from base import *
from .compiler import Compiler
from .exceptions import *
import click

@cli.command(help="Compile a project. \n\n Arguments: \n\n PROJECT: project path. \n\n TARGET: device target.")
@click.argument("project",type=click.Path())
@click.argument("target")
@click.option("--output","-o",default=False,help="output file path")
@click.option("--include","-I",default=[],multiple=True,help="additional include path (multi-value option)")
@click.option("--proj","-P",default=[],multiple=True,help="include project as library (multi-value option)")
@click.option("--define","-D",default=[],multiple=True,help="additional C macro definition (multi-value option)")
@click.option("--imports","-m",flag_value=True,default=False,help="only generate the list of imported modules")
def compile(project,target,output,include,define,imports,proj):
    if project.endswith(".py"):
        mainfile=project
        project=fs.dirname(project)
    else:
        mainfile = fs.path(project,"main.py")
    try:
        prj = fs.get_json(fs.path(project,".zproject"))
    except:
        fatal("Can't open project at",project)
    # create project import list
    prjs = {}
    for p in proj:
        zp = fs.path(p,".zproject")
        if not fs.exists(zp):
            warning("No project at",p)
            continue
        pj = fs.get_json(zp)
        if "package" in pj and "fullname" in pj["package"]:
            pmod = pj["package"]["fullname"]
        else:
            pmod = "local"
        if pmod not in prjs:
            prjs[pmod]=[]
        prjs[pmod].append(p)
    #TODO: check target is valid
    compiler = Compiler(mainfile,target,include,define,localmods=prjs)
    try:
        if not imports:
            binary, reprs = compiler.compile()
        else:
            modules, notfound = compiler.find_imports()
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

    if not imports:
        if not output:
            output=fs.path(project,"main.vbo")
        else:
            if fs.is_dir(output):
                output=fs.path(output,"main.vbo")
            else:
                if not output.endswith(".vbo"):
                    output=output+".vbo"
        info("Saving to",output)
        binary["repr"]=[rep.toDict() for rep in reprs]
        binary["project"]=project
        fs.set_json(binary,output)
        info("Compilation Ok")
    else:
        if env.human:
            table = []
            for k,v in modules.items():
                table.append([k,v])
            log_table(table,headers=["File","Module"])
        else:
            log_json([modules,list(notfound)])





