import click
from base.base import log_table, log_json, echo, error, pass_zcli
from base.cfg import env


@click.group()
def workspace():
    """Manage the Workspaces"""
    pass


@workspace.command()
@pass_zcli
def all(zcli):
    """List the  workspace"""
    wks = zcli.adm.workspace_all()
    print(wks)
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
@pass_zcli
def get(zcli, id):
    """Get a workspace"""
    try:
        workspace = zcli.adm.workspace_get(id)
        log_table([[workspace.Id, workspace.Name, len(workspace.Fleets)]], headers=["ID", "Name", "#fleets"])
    except Exception as e:
        error(e)


@workspace.command()
@click.argument('name')
@pass_zcli
def create(zcli, name):
    """Create a workspace"""
    zcli.sadm.workspace_create(name)
