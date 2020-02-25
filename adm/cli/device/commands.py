import click
from base.base import info

from ..helper import pass_adm

@click.group()
def device():
    """Manage the Devices"""
    pass


@device.command()
@click.option('--fleet-id', default=None, help='Fleet ID where the device is assigned')
@click.argument('name')
@pass_adm
def create(adm, fleet_id, name):
    """Create a device"""
    dev = adm.device_create(name, fleet_id)
    print(dev)


@device.command()
@click.argument('id')
@pass_adm
def get(adm, id):
    """Get a single device"""
    device = adm.device_get(id)
    info(device.Id)


@device.command()
@click.argument('id')
@pass_adm
def workspace(adm, id):
    """Get the workspace of a device"""
    adm.device_get_workspace(id)


@device.command()
@pass_adm
def all(adm):
    """Get all the devices"""
    for d in adm.device_all():
        info(d.Id)


@device.command()
@click.option('--fleet-id', default=None, help='Id of the  new fleet')
@click.option('--name', default=None, help='Name of the device')
@click.argument('id')
@pass_adm
def update(adm, id, fleet_id, name):
    """Update a device"""
    adm.device_update(id, name, fleet_id)
