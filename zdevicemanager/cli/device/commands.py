"""
.. _zdm-cmd-device:

*******
Devices
*******

In the ZDM a device is a peripheral that can execute Zerynth bytecode. In order to do so a device must be prepared and customized with certain attributes.
The main attributes of a device are:

* :samp:`uid` a unique id provided by the ZDM with the :ref:`device creation <zdm-cmd-device-create>` command
* :samp:`name` a name given by the user to the device in order to identify it

1. The first step to connect your device to the ZDM, once you are logged, is the device :ref:`creation <zdm-cmd-device-create>`.
2. Then you have to :ref:`create a key <zdm-cmd-device-create-key>` and :ref:`generate a jwt<zdm-cmd-device-generate-jwt>`.

There also are commands to :ref:`list your devices <zdm-cmd-device-get-all>`, to :ref:`get a single device info <zdm-cmd-device-get-device>`,
:ref:`update a device <zdm-cmd-device-update>` and to :ref:`list all device's key <zdm-cmd-device-get-all-keys>`


List of device commands:

* :ref:`Create <zdm-cmd-device-create>`
* :ref:`List devices <zdm-cmd-device-get-all>`
* :ref:`Get a single device <zdm-cmd-device-get-device>`
* :ref:`Create a device's key <zdm-cmd-device-create-key>`
* :ref:`List a device's keys <zdm-cmd-device-get-all-keys>`
* :ref:`Generate a password from a key <zdm-cmd-device-generate-jwt>`


The list of supported devices is available :ref:`here <doc-supported-boards>`

    """

import click
from zdevicemanager.base.base import log_table, pass_zcli, info, log_json
from zdevicemanager.base.cfg import env

from ..helper import handle_error


@click.group(help="Manage the devices")
def device():
    pass


@device.command(help="Create a new device")
@click.option('--fleet-id', default=None, help='Fleet ID where the device is assigned')
@click.argument('name')
@pass_zcli
@handle_error
def create(zcli, fleet_id, name):
    """
.. _zdm-cmd-device-create:

Device creation
---------------

To connect your device to the ZDM you must first create a new device on ZDM, to obtain a new device uid.
The creation command is: ::

    zdm device create name

where :samp:`name` is the name that you want to give to your new device

If you create your device using this command, it will be associated to your default fleet inside your default workspace.
If you want, you can choose to associate the device to another fleet with the optional argument:

:option:`--fleet-id uid`

If you want to associate the device to another fleet, see the :ref:`update command <zdm-cmd-device-update>`
    """
    dev = zcli.zdm.devices.create(name, fleet_id)
    if env.human:
        log_table([[dev.id, dev.name, dev.fleet_id]], headers=["ID", "Name", "fleet_id"])
    else:
        log_json(dev.toJson)


@device.command(help="Get all devices")
@pass_zcli
@handle_error
def all(zcli):
    """
.. _zdm-cmd-device-get-all:

List devices
------------

If you want to list all your devices, you can use this command to see a table with a device for each rows and 4 columns containing the device uid, name and the uid of the fleet and workspace containing them
to see all your devices use the command: ::

    zdm device all

    """

    table = []
    devs = zcli.zdm.devices.list()
    if env.human:
        for d in devs:
            table.append([d.id, d.name, d.fleet_id if d.fleet_id else "<none>", d.workspace_id])
        log_table(table, headers=["ID", "Name", "FleeId", "WorkspaceID"])
    else:
        dd = []
        for d in devs:
            dev = d.toJson
            dev.update({"workspace_id":d.workspace_id})
            dd.append(dev)
        log_json(dd)


@device.command(help="Get a single device by its uid")
@click.argument('id')
@pass_zcli
@handle_error
def get(zcli, id):
    """
.. _zdm-cmd-device-get-device:

Get device
----------

To get a single device information, you can use this command to see the device name and the uid of the fleet and the workspace that contain it. ::

    zdm device get uid

where :samp:`uid` is the device uid.

    """

    device = zcli.zdm.devices.get(id)
    if env.human:
        log_table([[device.id, device.name, device.fleet_id, device.workspace_id]],
                  headers=["ID", "Name", "FleetID", "WorkspaceID"])
    else:
        dev = device.toJson
        dev.update({"workspace_id":device.workspace_id})
        log_json(dev)


@device.command(help="Update a device")
@click.option('--fleet-id', default=None, help='Id of the new fleet')
@click.option('--name', default=None, help='Name of the device')
@click.argument('id')
@pass_zcli
@handle_error
def update(zcli, id, fleet_id, name):
    """
.. _zdm-cmd-device-update:

Update a device
---------------

Once you've created a device, you can use this command to update the device name, or to change the fleet uid associated to.
To update a device you just need its uid as argument, then you can use optional arguments to update its name or fleet uid.
Use the command: ::

    zdm device update uid

And the optional arguments are:

* :option:`--fleet-id uid` the uid of the fleet you want to associate the device to
* :option:`--name name` the name you want to give to the device

    """
    zcli.zdm.devices.update(id, name, fleet_id)
    info("Device [{}] updated correctly.".format(id))


@click.group(help="Manage the authentication key of a device")
def key():
    pass


@key.command(help="Create a new device key")
@click.argument("device-id")
@click.argument('key-name')
@pass_zcli
@handle_error
def create(zcli, key_name, device_id):
    """
.. _zdm-cmd-device-create-key:

Create a key
------------

To be able to connect your device to the ZDM you must create a key at first and then generate a password (as jwt token) from the created key.
You can generate different keys with different names for your devices with the command: ::

    zdm device key create uid name

Where :samp:`uid` is the device uid and :samp:`name` is the name you want to give to the key.
This command returns the generated key information as the key id, the name, the creation date and if the key has been revoked or not.

To connect your device to the ZDM, there is one last step to follow: :ref:`jwt generation <zdm-cmd-device-generate-jwt>`


    """

    key = zcli.zdm.keys.create(device_id, key_name)
    if env.human:
        log_table([[key.id, key.name, key.is_revoked, key.created_at]], headers=["ID", "Name", "Revoked", "CreatedAt"])
    else:
        log_json(key.toJson)


@key.command(help="Generate a password (jwt) from a key for your device")
@click.argument("device-id")
@click.argument('key-id')
@click.option('--expiration-days', default=31, help='Number of days after the key expires.')
@pass_zcli
@handle_error
def generate(zcli, device_id, key_id, expiration_days):
    """
.. _zdm-cmd-device-generate-jwt:

Generate a device's password (jwt)
---------------------------------

To be able to connect your device to the ZDM you must create a key at first and then generate a password (as jwt token) from the created key.
You can generate different keys with different names for your devices with the command: ::

    zdm device key generate uid kid

Where :samp:`uid` is the device uid and :samp:`kid` is the id of the key created.
This command returns the generated key information as the key id, the name, the creation date and if the key has been revoked or not.

    """

    key = zcli.zdm.keys.get(device_id, key_id)
    jwt = key.as_jwt(exp_delta_in_days=expiration_days)
    if env.human:
        log_table([[key.name, jwt, key.expire_at]], headers=["Key Name", "Password", "ExpireAt"])
    else:
        log_json(key.toJson)


@key.command(help="List all the keys of a device")
@click.argument("device-id")
@pass_zcli
@handle_error
def all(zcli, device_id):
    """
.. _zdm-cmd-device-get-all-keys:

List device keys
----------------

To see all the keys you have created for a device, use the command: ::

    zdm device key all uid

Where :samp:`uid` is the device uid.

This command returns for each key the id, the name, the creation date and if it's or not revoked.

    """
    keys = zcli.zdm.keys.list(device_id)
    if env.human:
        table = []
        for key in keys:
            table.append([key.id, key.name, key.is_revoked, key.created_at])  # key.as_jwt(), key.expire_at])
        log_table(table, headers=["ID", "Name", "Revoked", "CreatedAt"])
    else:
        log_json([k.toJson for k in keys])


device.add_command(key)
