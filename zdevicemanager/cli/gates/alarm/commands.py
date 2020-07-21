"""
.. _zdm-cmd-gates-alarm:


Alarm gates
===========

List of commands:

* :ref:`Create <zdm-cmd-gates-alarm-create>`
* :ref:`Update alarm <zdm-cmd-gates-alarm-update>`
* :ref:`List alarm gates <zdm-cmd-gates-alarm-get-all>`

    """

import click
from zdevicemanager.cli.helper import handle_error
from zdevicemanager.base.cfg import env
from zdevicemanager.base.base import log_table, pass_zcli, info, log_json


@click.group(help="Manage the export gates")
def alarm():
    pass


@alarm.command(help="Create a new alarm gate")
@click.argument('name')
@click.argument('workspace-id')
@click.argument('threshold')
@click.argument('email')
@click.argument('tags', nargs=-1)
@pass_zcli
@handle_error
def create(zcli, name, workspace_id, threshold, email, tags):

    """
.. _zdm-cmd-gates-alarm-create

Create alarm gate
-----------------

To create a new alarm gate (notifications about opened and closed conditions by devices) use the command: ::
    
    zdm gate alarm create name workspace_id threshold email tag(s)
    
where :samp:`name` is the name of the gate
:samp:`workspace_id` is the uid of the workspace
:samp:`threshold` is a int representing the minimum duration of a condition to be notified
:samp:`email` is the email where to receive notifications
:samp:`tag(s)` is a list of tags to filter on conditions labels

    """
    if len(tags) < 1:
        print("specify at least 1 tag")
        return

    gate_id = zcli.zdm.alarmgates.create(name, workspace_id, tags, threshold, email)
    info("Alarm gate [{}] created successfully.".format(gate_id))


@alarm.command(help="Update an alarm gate")
@click.argument('gate-id')
@click.option('--name', help='To change gate name')
@click.option('--tags', multiple=True, help='To replace gate tags')
@click.option('--threshold', help='To change gate threshold', type=int)
@pass_zcli
@handle_error
def update(zcli, gate_id, name, tags, threshold):

    """
.. _zdm-cmd-gates-alarm-update

Update alarm gate
-----------------

To update an alarm gate use the command: ::

    zdm gate alarm update gate_id

to change gate's configuration using the following options: ::
* :option:`--name` to change the gate's name
* :option:`--tag` (multiple option) to replace gate's tag array
* :option:`--threshold` to change the gate's threshold

    """
    zcli.zdm.alarmgates.update(gate_id, name, tags, threshold)
    info("Gate [{}] updated correctly.".format(gate_id))


@alarm.command(help="Get all the alarm gates of a workspace")
@click.option('--status', default="active", type=click.Choice(['active', 'disabled']), help="Filter gates by status.")
@click.argument('workspace-id')
@pass_zcli
@handle_error
def all(zcli, workspace_id, status):
    """
.. _zdm-cmd-gates-alarm-get-all:

List export gates
-----------------

To see the list of the alarm gates use the command: ::

    zdm gate alarm all workspace_id

where :samp:`workspace_id` is the uid of the workspace

To add filters on gates use the following options:

* :option:`--status active|disabled` to filter on gate's status

    """
    gates = zcli.zdm.gates.list(workspace_id, status, 'alarm')
    table = []

    if env.human:
        for gate in gates:
            table.append([gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled])
        log_table(table, headers=["ID", "Name", "Period", "Status", "LastSchedule"])

    else:
        log_json([gate.toJson for gate in gates])
