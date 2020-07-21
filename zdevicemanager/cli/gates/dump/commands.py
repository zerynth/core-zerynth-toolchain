"""
.. _zdm-cmd-gates-export:


Export gates
============

List of commands:

* :ref:`Create <zdm-cmd-gates-export-create>`
* :ref:`Update export gate <zdm-cmd-gates-export-update>`
* :ref:`List export gates <zdm-cmd-gates-export-get-all>`

    """

import click
from zdevicemanager.cli.helper import handle_error
from zdevicemanager.base.cfg import env
from zdevicemanager.base.base import log_table, pass_zcli, info, log_json


@click.group(help="Manage the export gates")
def export():
    pass


@export.command(help="Create a new export gate. ")
@click.argument('name')
@click.argument('type')
@click.argument("frequency")
@click.argument('workspace-id')
@click.argument('email')
@click.option('--tag', multiple=True)
@click.option('--fleet', multiple=True)
@click.option('--export-name', default="", help="Name of the export")
@click.option('--day', default='1', help="Day for the export (0 Sunday... 6 Saturday)",
              type=click.Choice(['0', '1', '2', '3', '4', '5', '6']))
@pass_zcli
@handle_error
def create(zcli, name, export_name, type, frequency, day, workspace_id, email, tag, fleet):
    """
.. _zdm-cmd-gates-export-create:

Export gate creation
--------------------

To create a new export gate use the command: ::

    zdm gate export create name type frequency workspace_id email

where :samp:`name` is the gate name
:samp:`type` is the export type (json, csv)
:samp:`frequency` is the export frequency [daily, weekly]
:samp:`workspace_id` is the uid of the workspace to receive data from
:samp:`email` is the email where to receive the link to download the export

It's also possible to add filters on data using the following options:

:option:`--tag` To specify a tag to filter data (one or more)
:option:`--fleet` To specify a fleet to filter data (one or more)
:option:`--export-name` To specify the export's name
:option: '--day' To specify the day (if frequency is weekly) [0 Sunday... 6 Saturday]
    """
    tags = []
    fleets = []

    for t in tag:
        tags.append(t)

    for f in fleet:
        fleets.append(f)

    if export_name == "":
        export_name = name

    gate_id = zcli.zdm.exportgates.create(name, export_name, type, frequency, int(day), workspace_id, email, tags, fleets)
    info("Export gate [{}] created successfully.".format(gate_id))


@export.command(help="Get all the export gates of a workspace")
@click.option('--status', default="active", type=click.Choice(['active', 'disabled']), help="Filter gates by status.")
@click.argument('workspace-id')
@pass_zcli
@handle_error
def all(zcli, workspace_id, status):
    """
.. _zdm-cmd-gates-export-get-all:

List export gates
-----------------

To see the list of the export gates use the command: ::

    zdm gate export all workspace_id

where :samp:`workspace_id` is the uid of the workspace

It's also possible to add filters on gates using the following options:

* :option:`--status active|disabled` to filter on gate's status

    """
    gates = zcli.zdm.gates.list(workspace_id, status, 'dump')
    table = []

    if env.human:
        for gate in gates:
            table.append([gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled])
        log_table(table, headers=["ID", "Name", "Period", "Status", "LastSchedule"])

    else:
        log_json([gate.toJson for gate in gates])


@export.command(help="Update an export gate")
@click.argument('gate-id')
@click.option('--name', help='To change webhook name')
@click.option('--cron', help='To change webhook period', type=int)
@click.option('--dump-type', help='To change webhook url', type=click.Choice(['json', 'csv']))
@click.option('--email', help='To change notifications email')
@click.option('--tag', multiple=True, help='To replace gate tags')
@pass_zcli
@handle_error
def update(zcli, gate_id, name=None, cron=None, dump_type=None, email=None, tag=None):

    """
.. _zdm-cmd-gates-export-update

Update export
--------------

To update an export gate use the command: ::

    zdm gate export update gate_id

To change gate's configuration use the following options: ::
* :option:`--name` to change the gate name
* :option:`--cron` to change the gate period (cron string hour day)
* :option:`--dump_type` to change the dump format (json, csv)
* :option:`--email` to change the notifications email
* :option:`--tag` (multiple option) to replace webhook tag array

    """
    zcli.zdm.exportgates.update(gate_id, name, cron, dump_type, email, tag)
    info("Gate [{}] updated correctly.".format(gate_id))
