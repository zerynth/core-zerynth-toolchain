"""
.. _zdm-cmd-events:

******
Events
******

In the ZDM events are used in devices to notify the occurrence of certain conditions.


List of device commands:

* :ref:`Get events <zdm-cmd-events-get>`

    """
import click
from zdevicemanager.base.base import log_table, log_json, pass_zcli, info

from ..helper import handle_error

@click.group(help="Manage the events")
def event():
    pass


@event.command(help="Get all the event sent by devices of a workspace")
@click.argument('workspace-id')
@click.option('--device-id', default=None, help='Device ID to filter events')
@click.option('--start', default=None, help='start date filter (RFC3339)')
@click.option('--end', default=None, help='end date filter (RFC3339)')
@pass_zcli
@handle_error
def list(zcli, workspace_id, device_id, start, end):
    """
.. _zdm-cmd-workspace-events-get:

Get events
----------

To get all the events of a workspace use the command: ::

    zdm events uid

where :samp:`uid` is the uid of the workspace.

You can also filter result adding the options:
* :option:`--device-id`
* :option:`--start`
* :option:`--end`

    """

    events = zcli.zdm.events.get(workspace_id, device_id, start=start, end=end)
    if len(events) > 0:
        table = []
        for event in events:
            table.append([event.Name, event.Payload, event.DeviceId, event.Timestamp])
        log_table(table, headers=["Name", "Payload", "Device", "Timestamp"])
    else:
        info("No events present.")
