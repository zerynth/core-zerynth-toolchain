import click
import base64
from base.base import log_table, pass_zcli, info
from base.jwt.api_jwt import encode
import   time
@click.group()
def device():
    """Manage the Devices"""
    pass


@device.command()
@click.option('--fleet-id', default=None, help='Fleet ID where the device is assigned')
@click.argument('name')
@pass_zcli
def create(zcli, fleet_id, name):
    """Create a device"""
    dev = zcli.adm.device_create(name, fleet_id)
    print(dev)


@device.command()
@click.argument('id')
@pass_zcli
def get(zcli, id):
    """Get a single device"""
    device = zcli.adm.device_get(id)
    log_table([[device.Id, device.Name]], headers=["ID", "Name"])


@device.command()
@click.argument('id')
@pass_zcli
def workspace(zcli, id):
    """Get the workspace of a device"""
    workspace = zcli.adm.device_get_workspace(id)
    log_table([[workspace.Id, workspace.Name]], headers=["ID", "Name"])


@device.command()
@pass_zcli
def all(zcli):
    """Get all the devices"""
    table = []
    for d in zcli.adm.device_all():
        table.append([d.Id, d.Name, d.FleetID if d.FleetID else "<none>"])
    log_table(table, headers=["ID", "Name", "FleeId"])


@device.command()
@click.option('--fleet-id', default=None, help='Id of the new device')
@click.option('--name', default=None, help='Name of the device')
@click.argument('id')
@pass_zcli
def update(zcli, id, fleet_id, name):
    """Update a device"""
    zcli.adm.device_update(id, name, fleet_id)
    info("Device ", device.Id, " updated correctly")


@device.command()
@click.argument("id")
@click.argument('Name')
@pass_zcli
def key(zcli, name, id):
    """Provision the devie with a new key"""
    keydevice = zcli.adm.device_create_key(name, id)

    key = base64.b64decode(keydevice.raw)
    encoded_jwt = encode({'sub': id, "user": id, "key": keydevice.Id, "exp": int(time.time())+3600*24*30}, key,
                             algorithm='HS256')
    info("Jwt Device: " , encoded_jwt.decode("utf-8"))