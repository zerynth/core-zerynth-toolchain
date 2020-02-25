import click
from base.base import info
from ..helper import pass_adm

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
    for f in adm.fleet_all():
        info(f.id)

@fleet.command()
@click.argument('id')
@pass_adm
def get(adm, id):
    """Get a single fleet"""
    fleet = adm.fleet_get(id)
    info("Get fleet", fleet.name)