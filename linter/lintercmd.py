from base import *
import click
import json
from . import autopep8

@cli.group()
def linter():
    pass


@linter.command()
@click.argument("data")
@click.option("-f","file",flag_value=True,default=False)
@click.option("--json","__json",flag_value=True,default=False)
def pep8(data,file,__json):
    if file:
        data = fs.readfile(data)
    else:
        if not data.startswith("\"") or not data.endswith("\""): data="\""+data+"\""
        data = json.loads(data)
    res = autopep8.fix_code(data,options={"aggressive":1,"max_line_length":120})
    if __json:
        log(json.dumps(res))
    else:
        log(res)
