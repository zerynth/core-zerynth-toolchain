import click
from base.base import log_table, info, pass_zcli


@click.group()
def fleet():
    """Manage the Fleet"""
    pass


@fleet.command()
@click.argument('name')
@click.argument('workspaceid')
@pass_zcli
def create(zcli, name, workspaceid):
    """Create a fleet"""
    fleet = zcli.adm.fleet_create(name, workspaceid)
    log_table([[fleet.id, fleet.name, fleet.WorkspaceId]], headers=["ID", "Name", "WorkspaceID"])



@fleet.command()
@pass_zcli
def all(zcli):
    """Get all the fleets"""
    table = []
    for f in zcli.adm.fleet_all():
        print(f.Devices)
        table.append([f.id, f.name, f.WorkspaceId if f.WorkspaceId else "<none>", [d.id for d in f.Devices]])
    log_table(table, headers=["ID", "Name", "WorkspaceID", "Devices"])


@fleet.command()
@click.argument('id')
@pass_zcli
def get(zcli, id):
    """Get a single fleet"""
    fleet = zcli.adm.fleet_get(id)

    info("Get fleet", fleet.name)
