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
@pass_zcli
@handle_error
def create(zcli, key_name, device_id):
    """Create a device key."""
    key = zcli.adm.keys.create(device_id, key_name)
    log_table([[key.id, key.name, key.is_revoked, key.created_at]], headers=["ID", "Name", "Revoked", "CreatedAt"])

@key.command()
@click.argument("device-id")
@click.argument('key-id')
@click.option('--expiration-days', default=31, help='Number of days after the key expires.')
@pass_zcli
@handle_error
def generate(zcli, device_id, key_id, expiration_days):
    """Generate a password  (Jwt) from a key."""
    key = zcli.adm.keys.get(device_id, key_id)
    jwt = key.as_jwt(exp_delta_in_days=expiration_days)
    log_table([[key.name, jwt, key.expire_at]], headers=["Key Name", "Password", "ExpireAt"])

@key.command()
@click.argument("device-id")
@pass_zcli
@handle_error
def all(zcli, device_id):
    """List the keys."""
    keys = zcli.adm.keys.list(device_id)
    table = []
    for key in keys:
        table.append([key.id, key.name, key.is_revoked, key.created_at])  # key.as_jwt(), key.expire_at])
    log_table(table, headers=["ID", "Name", "Revoked", "CreatedAt"])


device.add_command(key)
