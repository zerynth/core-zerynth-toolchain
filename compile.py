import click
from base import *
from compiler import *

@cli.group()
def compile():
    echo("Compile")

@compile.command()
def clean():
    echo("Clean")

@compile.command()
def debug():
    echo("Debug")

@compile.group()
def fuffa():
    echo("fuffa")

@fuffa.command()
def nah():
    echo("nah")