import click

from ..helper import pass_adm
from base.base import log_table, log_json, echo, error
from base.cfg import env

@click.group()
def workspace():
    """Manage the Workspaces"""
    pass


@workspace.command()
@pass_adm
def all(adm):
    wks = adm.workspace_all()
    if env.human:
        table = []
        for ws in wks:
            table.append([ws.Id, ws.Name])
        log_table(table, headers=["ID", "Name"])
    else:
        for ws in wks:
            log_json(ws.toJSON())


@workspace.command()
@click.argument('id')
@pass_adm
def get(adm, id):
    """Get a workspace"""
    try:
        workspace = adm.workspace_get(id)
        echo(workspace.Id)
    except Exception as e:
       error(e)



@workspace.command()
@click.argument('name')
@pass_adm
def create(adm, name):
    """Create a workspace"""
    adm.workspace_create(name)
