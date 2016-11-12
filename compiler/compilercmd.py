from base import *
from .compiler import Compiler
from .exceptions import *
import click

@cli.command()
@click.argument("project",type=click.Path())
@click.argument("target")
@click.option("--output","-o",default=False)
@click.option("--include","-I",default=[],multiple=True)
@click.option("--define","-D",default=[],multiple=True)
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
    except Exception as e:
        raise e
    if not output:
        output=fs.basename(project)+".vbo"
    elif not output.endswith(".vbo"):
        output+=".vbo"
    info("Saving to",output)
    binary["repr"]=[rep.toDict() for rep in reprs]
    fs.set_json(binary,output)
    info("Compilation Ok")





