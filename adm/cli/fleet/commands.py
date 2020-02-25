import click
from base.base import info
from ..helper import pass_adm
from base.base import log_table, log_json, echo, error

@click.group()
def fleet():
    """Manage the Fleet"""
    pass

@fleet.command()
@click.argument('name')
@click.argument('workspaceid')
@pass_adm
def create(adm, name, workspaceid):
    """Create a fleet"""
    fleet = adm.fleet_create(name, workspaceid)
    info("Created fleet:", fleet.name)

@fleet.command()
@pass_adm
def all(adm):
    """Get all the fleets"""
    table = []
    for f in adm.fleet_all():
        table.append([f.Id, f.Name, f.WorkspaceId if f.WorkspaceId else "<none>"])
    log_table(table, headers=["ID", "Name", "WorkspaceID"])


@fleet.command()
@click.argument('id')
@pass_adm
def get(adm, id):
    """Get a single fleet"""
    fleet = adm.fleet_get(id)
    info("Get fleet", fleet.name)