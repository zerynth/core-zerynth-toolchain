import click
from base.base import log_table, info, pass_zcli


@click.group()
def fleet():
    """Manage the Fleet"""
    pass

@fleet.command()
@pass_zcli
def all(zcli):
    """Get all the fleets"""
    table = []
    for f in zcli.adm.fleets.list():
        table.append([f.id, f.name, f.workspace_id if f.workspace_id else "<none>", f.devices])
    log_table(table, headers=["ID", "Name", "WorkspaceId", "Devices"])


@fleet.command()
@click.argument('name')
@click.argument('workspaceid')
@pass_zcli
def create(zcli, name, workspaceid):
    """Create a fleet"""
    fleet = zcli.adm.fleets.create(name, workspaceid)
    log_table([[fleet.id, fleet.name, fleet.workspace_id]], headers=["ID", "Name", "WorkspaceID"])


@fleet.command()
@click.argument('id')
@pass_zcli
def get(zcli, id):
    """Get a single fleet"""
    fleet = zcli.adm.fleets.get(id)
    log_table([[fleet.id, fleet.name, fleet.workspace_id, fleet.devices]], headers=["ID", "Name", "WorkspaceID", "Devices"])
