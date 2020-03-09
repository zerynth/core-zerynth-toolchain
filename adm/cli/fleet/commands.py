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
    info("Created fleet:", fleet.name)


@fleet.command()
@pass_zcli
def all(zcli):
    """Get all the fleets"""
    table = []
    for f in zcli.adm.fleet_all():
        table.append([f.Id, f.Name, f.WorkspaceId if f.WorkspaceId else "<none>"])
    log_table(table, headers=["ID", "Name", "WorkspaceID"])


@fleet.command()
@click.argument('id')
@pass_zcli
def get(zcli, id):
    """Get a single fleet"""
    fleet = zcli.adm.fleet_get(id)
    info("Get fleet", fleet.name)
