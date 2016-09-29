import click
import sys
import traceback
import time
import json

__all__ =['Critical','Error','Warning','Info','echo','cli','error','warning','info','log','critical','fatal','add_init','init_all','sleep']


## GLOBAL OPTIONS
_options = {
    "colors": True,
    "traceback": True
}

################### json special type encoder
class ZjsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

## Styles
_styles = {
    "Critical":{"fg":"magenta","bold":True},
    "Error":{"fg":"red","bold":True},
    "Warning":{"fg":"yellow"},
    "Info":{"fg":"green"}
}


_init_fns = []

def add_init(init,prio=None):
    global _init_fns
    if prio is None or prio<0:
        _init_fns.append(init)
    else:
        _init_fns = [init]+_init_fns

def init_all():
    for ii in _init_fns:
        ii()

class Style():
    def __init__(self,val):
        self.val = val

    def __str__(self):
        if _options["colors"]:
            return click.style(str(self.val),**_styles[self.__class__.__name__])
        else:
            return str(self.val)

class Critical(Style):
    pass

class Error(Style):
    pass

class Warning(Style):
    pass

class Info(Style):
    pass

## The magical Echo

def echo(*args,**kwargs):
    sep = kwargs.get("sep"," ")
    end = kwargs.get("end","\n")
    if args:
        click.echo(str(args[0]),nl=False)
        for i in range(1,len(args)):
            click.echo(str(sep),nl=False)
            click.echo(str(args[i]),nl=False)
    click.echo(str(end),nl=False)


def critical(*args,**kwargs):
    if "exc" in kwargs:
        exc = kwargs.pop("exc")
    else:
        exc = None
    echo(Critical("[fatal]   >"),*args,**kwargs)
    if exc and _options["traceback"]:
        traceback.print_exc()
    sys.exit(1)
    

def fatal(*args,**kwargs):
    echo(Fatal("[error]   >"),*args,**kwargs)
    sys.exit(1)
def error(*args,**kwargs):
    echo(Error("[error]   >"),*args,**kwargs)

def warning(*args,**kwargs):
    echo(Warning("[warning] >"),*args,**kwargs)

def info(*args,**kwargs):
    echo(Info("[info]    >"),*args,**kwargs)

log = echo

def sleep(n):
    time.sleep(n)
## Main entrypoint gathering 

@click.group()
@click.option("-v","verbose",flag_value=True,default=False,help="verbose")
@click.option("--colors/--no-colors","nocolors",default=True,help="enable/disable colors")
@click.option("--traceback/--no-traceback","notraceback",default=True,help="enable/disable exception traceback printing on criticals")
def cli(verbose,nocolors,notraceback):
    _options["colors"]=nocolors
    _options["traceback"]=notraceback
    _options["verbose"]=verbose
