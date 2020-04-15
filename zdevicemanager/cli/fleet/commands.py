"""
.. _zdm-cmd-fleet:


Fleets
======

In the ZDM a fleet is a set of devices. When you log in for the first time, a 'default' fleet will be created.
The main attributes of a fleet are:

* :samp:`uid`, a unique id provided by the ZDM after the :ref:`fleet creation <zdm-cmd-fleet-create>` command
* :samp:`name`, a name given by the user to the fleet in order to identify it


List of fleet commands:

* :ref:`Create <zdm-cmd-fleet-create>`
* :ref:`List fleets <zdm-cmd-fleet-get-all>`
* :ref:`Get a single fleet <zdm-cmd-fleet-get-fleet>`

    """

import click
from zdevicemanager.base.base import log_table, info, pass_zcli, log_json
from zdevicemanager.base.cfg import env
from ..helper import handle_error


@click.group(help="Manage the Fleets")
def fleet():
    pass


@fleet.command(help="Create a new fleet")
@click.argument('name')
@click.argument('workspaceid')
@pass_zcli
@handle_error
def create(zcli, name, workspaceid):
    """
.. _zdm-cmd-fleet-create:

Fleet creation
--------------

To create a new fleet of devices inside a workspace use the command: ::

    zdm fleet create name workspace_uid

where :samp:`name` is the name you want to give to your new fleet and :samp:`workspace_id` is the uid of the workspace that will contain the fleet.

    """
    fleet = zcli.zdm.fleets.create(name, workspaceid)
    if env.human:
        log_table([[fleet.id, fleet.name, fleet.workspace_id]], headers=["ID", "Name", "WorkspaceID"])
    else:
        log_json(fleet.toJson)


@fleet.command(help="Get all the fleets")
@pass_zcli
@handle_error
def all(zcli):
    """
.. _zdm-cmd-fleet-get-all:

List fleets
------------

If you want to list all your fleets, you can use this command to have information about the associated workspace, and the list of devices inside: ::

    zdm fleet all

    """
    table = []
    fleets = zcli.zdm.fleets.list()
    if env.human:
        for f in fleets:
            table.append([f.id, f.name, f.workspace_id if f.workspace_id else "<none>", f.devices])
        log_table(table, headers=["ID", "Name", "WorkspaceId", "Devices"])
    else:
        log_json([f.toJson for f in fleets])


@fleet.command(help="Get a single fleet by its uid")
@click.argument('id')
@pass_zcli
@handle_error
def get(zcli, id):
    """
.. _zdm-cmd-fleet-get-fleet:

Get fleet
---------

To get a single fleet information, you can use this command to see its name, the uid of the workspace that contains it and the list of devices inside::

    zdm fleet get uid

where :samp:`uid` is the fleet uid

    """
    fleet = zcli.zdm.fleets.get(id)
    log_table([[fleet.id, fleet.name, fleet.workspace_id, fleet.devices]],
              headers=["ID", "Name", "WorkspaceID", "Devices"])
