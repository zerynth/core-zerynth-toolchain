"""
.. _zdm-cmd-workspace:

Workspaces
==========

In the ZDM a workspace is the root node in Zerynth device management. A workspace represents a project containing fleets of devices.
The main attributes of a workspace are:

* :samp:`uid` a unique id provided by the ZDM with the :ref:`workspace creation <zdm-cmd-workspace-create>` command
* :samp:`name` a name given by the user to the workspace in order to identify it
* :samp:`description` a string given by the user to describe the project

At your first log in, a 'default' workspace containing a 'default' fleet will be created.


List of workspace commands:

* :ref:`Create <zdm-cmd-workspace-create>`
* :ref:`List workspaces <zdm-cmd-workspace-get-all>`
* :ref:`Get a single workspace <zdm-cmd-workspace-get-workspace>`
* :ref:`Get data <zdm-cmd-workspace-data>`
* :ref:`List firmwares <zdm-cmd-workspace-firmware>`
* :ref:`List workspace tags <zdm-cmd-workspace-tag>`


The list of supported devices is available :ref:`here <doc-supported-boards>`

    """

import click
from zdevicemanager.base.base import log_table, log_json, pass_zcli, info
from zdevicemanager.base.cfg import env

from ..helper import handle_error


@click.group(help="Manage the workspaces")
def workspace():
    pass


@workspace.command(help="List all the workspaces")
@pass_zcli
@handle_error
def all(zcli):
    """
.. _zdm-cmd-workspace-get-all:

List workspaces
---------------

To see the list of all your workspaces, use the command: ::

    zdm workspace all

    """
    wks = zcli.zdm.workspaces.list()
    if env.human:
        table = []
        for ws in wks:
            table.append([ws.id, ws.name, ws.description, ws.fleets, ws.devices])
        log_table(table, headers=["ID", "Name", "Description" "Fleets", "Devices"])
    else:
        log_json([wk.toJson for wk in wks])

@workspace.command(help="Get a workspace by its uid")
@click.argument('id')
@pass_zcli
@handle_error
def get(zcli, id):
    """
.. _zdm-cmd-workspace-get-workspace:

Get workspace
-------------

To get a single workspace information, you can use this command: ::

    zdm workspace get uid

where :samp:`uid` is the workspace uid.

    """
    ws = zcli.zdm.workspaces.get(id)
    if env.human:
        data = [ws.id, ws.name, ws.description, ws.fleets, ws.devices]
        log_table([data], headers=["ID", "Name", "Description", "Fleets", "Devices"])
    else:
        log_json(ws.toJson)


@workspace.command(help="Create a new workspace")
@click.argument('name')
@click.option('--description', default="", type=click.STRING, help="Small description af the workspace.")
@pass_zcli
@handle_error
def create(zcli, name, description):
    """
.. _zdm-cmd-workspace-create:

Workspace creation
------------------

To create a new workspace on the ZDM use the command: ::

    zdm workspace create name

where :samp:`name` is the name that you want to give to your new workspace

You can also insert a description of your workspace adding the option :option:`--description desc`

    """
    wks = zcli.zdm.workspaces.create(name, description)
    if env.human:
        log_table([[wks.id, wks.name, wks.description]], headers=["ID", "Name", "Description"])
    else:
        log_json(wks.toJson)


@workspace.command(help="Get all the tags of a workspace")
@click.argument('workspace-id')
@pass_zcli
@handle_error
def tags(zcli, workspace_id):
    """
.. _zdm-cmd-workspace-tag:

List tags
---------

When a device publish data to the ZDM it label them with a string called tag. With the following command you can see all the tags
that devices associated to your workspace used as data label. ::

    zdm workspace tags uid

where :samp:`uid` is the uid of the workspace

    """
    tags = zcli.zdm.data.list(workspace_id)
    if env.human:
        if len(tags) > 0:
            log_table([[tags]], headers=["Tags"])
        else:
            info("Empty tags for workspace {}.".format(workspace_id))
    else:
        log_json([tag.toJson for tag in tags])

@workspace.command(help="Get all the data of a workspace associated to a tag")
@click.argument('workspace-id')
@click.argument('tag')
@click.option('--device-id', default=None, help='Device ID to filter events')
@click.option('--start', default=None, help='start date filter (RFC3339)')
@click.option('--end', default=None, help='end date filter (RFC3339')
@pass_zcli
@handle_error
def data(zcli, workspace_id, tag, device_id, start, end):

    """
.. _zdm-cmd-workspace-data:

Get data
--------

To get all the data of a workspace associated to a tag use the command: ::

    zdm workspace data uid tag

where :samp:`uid` is the uid of the workspace.

You can also filter result adding the options:
* :option:`--device-id`
* :option:`--start`
* :option:`--end`

    """

    tags = zcli.zdm.data.get(workspace_id, tag, device_id=device_id, start=start, end=end)
    if env.human:
        if len(tags) > 0:
            table = []
            for tag in tags:
                table.append([tag.Tag, tag.Payload, tag.DeviceId, tag.Timestamp])
            log_table(table, headers=["Tag", "Payload", "Device", "Timestamp"])
        else:
            info("No data present for to tag [{}].".format(tag))
    else:
        log_json([tag.toJson for tag in tags])

@workspace.command(help="Get all the firmwares of a workspace")
@click.argument('workspace-id')
@pass_zcli
@handle_error
def firmwares(zcli, workspace_id):
    """
.. _zdm-cmd-workspace-firmware:

List firmwares
--------------

To have a list of the firmwares you uploaded to the ZDM associated to a workspace use the command: ::

    zdm workspace tags uid

where :samp:`uid` is the uid of the workspace.

    """
    table = []
    firmwares = zcli.zdm.firmwares.list(workspace_id)
    if env.human:
        for d in firmwares:
            table.append([d.id, d.version, d.metadata, d.workspace_id])
        log_table(table, headers=["ID", "Version", "Metadata", "WorkspaceID"])
    else:
        log_json([frm.toJson for frm in firmwares])

