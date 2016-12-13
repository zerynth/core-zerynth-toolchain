from base import *
import click
import json
from . import autopep8

@cli.group(help="Python linter.")
def linter():
    pass

@linter.command(help="Check pep8 code conventions. \n\n Arguments: \n\n DATA: Data to check.")
@click.argument("data")
@click.option("-f","--file",flag_value=True,default=False,help="if given, data is interpreted as a path to a file")
@click.option("--json","__json",flag_value=True,default=False,help="select JSON output")
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
