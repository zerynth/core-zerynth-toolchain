"""
.. module:: Linter


Linter
======

The Zerynth Linter permits to check Python code against some of the style conventions.

In z-linter command is present a ``--help`` option to show to the users a brief description of the related command and its syntax including argument and option informations.

The command return several log messages grouped in 4 main levels (info, warning, error, fatal) to inform the users about the results of the operation. 
The action that can be executed on Zerynth Linter is:

* :ref:`pep8<Linter Command - pep8>`: to check Python script with pep8 style convention

Linter Command - pep8
---------------------

This command is used to check a Python source code against Python Enhancement Proposals 8 (pep8)
coding convention from the command line with this syntax: ::

    Syntax:   ./ztc linter pep8 data --file --json
    Example:  ./ztc linter pep8 script.py --file --json

This command take as input the following arguments:
    * **data** (str) --> data to check in raw string format or in path file format (**required**)
    * **file** (bool) --> select data source: if true is from a file, else is from string (**optional**, default=False)
    * **json** (bool) --> flag for output format: if true is in json format (**optional**; default=False)

**Errors**:
    * Missing required input data
"""
from base import *
import click
import json
from . import autopep8

@cli.group(help="Python style checker.")
def linter():
    pass
""" Python Enhancement Proposals pep8 is a tool to check your Python code against some of the style conventions in PEP 8."""

@linter.command(help="Check pep8 code conventions. \n\n Arguments: \n\n DATA: Data to check.")
@click.argument("data")
@click.option("-f","--file",flag_value=True,default=False,help="If true data must be a file.")
@click.option("--json","__json",flag_value=True,default=False,help="If true output in json format.")
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
