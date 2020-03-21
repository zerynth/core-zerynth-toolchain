import click
from base.base import log_table, pass_zcli, info

from ..helper import handle_error


@click.group()
def device():
    """Manage the Devices"""
    pass


@device.command()
@pass_zcli
@handle_error
def all(zcli):
    """Get all the devices"""
    table = []
    for d in zcli.adm.devices.list():
        table.append([d.id, d.name, d.fleet_id if d.fleet_id else "<none>", d.workspace_id])
    log_table(table, headers=["ID", "Name", "FleeId", "WorkspaceID"])


@device.command()
@click.option('--fleet-id', default=None, help='Fleet ID where the device is assigned')
@click.argument('name')
@pass_zcli
@handle_error
def create(zcli, fleet_id, name):
    """Create a device"""
    dev = zcli.adm.devices.create(name, fleet_id)
    log_table([[dev.id, dev.name, dev.fleet_id]], headers=["ID", "Name", "fleet_id"])


@device.command()
@click.argument('id')
@pass_zcli
@handle_error
def get(zcli, id):
    """Get a single device"""
    device = zcli.adm.devices.get(id)
    log_table([[device.id, device.name, device.fleet_id, device.workspace_id]],
               headers=["ID", "Name", "FleetID", "WorkspaceID"])

@device.command()
@click.option('--fleet-id', default=None, help='Id of the new fleet')
@click.option('--name', default=None, help='Name of the device')
@click.argument('id')
@pass_zcli
@handle_error
def update(zcli, id, fleet_id, name):
    """Update a device"""
    zcli.adm.devices.update(id, name, fleet_id)
    info("Device [{}] updated correctly.".format(id))


@click.group()
def key():
    """Manage the authentication key of a Device"""
    pass


@key.command()
@click.argument("device-id")
@click.argument('key-name')
@click.option('--as-jwt', default=True, help='Generate a new Jwt fo the key')
@click.option('--expiration-days', default=31, help='Expiration in days')
@pass_zcli
def create(zcli, key_name, device_id, as_jwt, expiration_days):
    """Generate a new authetication key"""
    keydevice = zcli.adm.device_create_key(key_name, device_id)
    if as_jwt:
        keydevice.set_exp_time(expiration_days)
        jwt = keydevice.as_jwt()
        log_table([[device_id, keydevice.id, keydevice.name, jwt, keydevice.Expiration]],
                  headers=["Device Id", "Key Id", "Key Name", "Password", "Expiration"])
    else:
        log_table([[device_id, keydevice.id, keydevice.name]], headers=["Device Id", "Key Id", "Key Name"])


@key.command()
@click.argument("device-id")
@pass_zcli
def all(zcli, device_id):
    """List the authetication key of a device"""
    keys = zcli.adm.device_all_key(device_id)
    table = []
    for key in keys:
        table.append([key.id, key.name])  # key.as_jwt(), key.Expiration])
    log_table(table, headers=["ID", "Name"])


device.add_command(key)
