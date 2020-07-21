"""
.. _zdm-cmd-gates:


Gates
=====

Using the ZDM it's possible to send out devices' data through gates.
ZDM allows to activate a webhook to receive all the data sent on a specific tag in a workspace or
to create an export gate to receive periodically a link to download them.
Crerating an alarm gate allows to be notified on conditions opened by devices.
It's also possible to use webhooks to send devices data to Ubidots dashboards.

    """

import click
from zdevicemanager.base.base import log_table, pass_zcli, info
from zdevicemanager.cli.helper import handle_error


@click.group(help="Manage the gates")
def gate():
    pass

#
# @gate.command(help="Get a single gate")
# @click.argument('gate-id')
# @pass_zcli
# @handle_error
# def get(zcli, gate_id):
#     """
# .. _zdm-cmd-gates-get:
#
# Get a gate
# -------------
#
# To see information about a single gate use the command: ::
#
#     zdm gate get gate_id
#
# where :samp:`gate_id` is the uid of the gate.
#
#     """
#     gate = zcli.zdm.gates.get(gate_id)
#     log_table([[gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled, gate.configuration]],
#               headers=["ID", "Name", "Period", "Status", "LastSchedule", "Info"])
#
#
# @gate.command(help="Disable a gate by its uid")
# @click.argument('gate-id')
# @pass_zcli
# @handle_error
# def disable(zcli, gate_id):
#     """
# .. _zdm-cmd-gates-disable:
#
# Disable a gate
# --------------
#
# To disable a gate use the command: ::
#
#     zdm gate disable webhook_id
#
# where :samp:`gate_id` is the uid of the gate.
#
#     """
#     res = zcli.zdm.gates.update_gate_status(gate_id, status="disabled")
#     if res is not None:
#         info("Gate ", gate_id, " succesfully disabled.")
#
#
# @gate.command(help="Enable a gate by its uid")
# @click.argument('gate-id')
# @pass_zcli
# @handle_error
# def enable(zcli, gate_id):
#     """
# .. _zdm-cmd-gates-enable:
#
# Enable a gate
# -------------
#
# To enable a gate use the command: ::
#
#     zdm gate enable gate_id
#
# where :samp:`gate_id` is the uid of the gate.
#
#     """
#     res = zcli.zdm.gates.update_gate_status(gate_id, status="active")
#     if res is not None:
#         info("Gate ", gate_id, " successfully enabled.")
#
#
# @gate.command(help="Delete a gate")
# @click.argument('gate-id')
# @pass_zcli
# @handle_error
# def delete(zcli, gate_id):
#     """
# .. _zdm-cmd-gates-delete:
#
# Delete a gate
# --------------
#
# To delete a gate use the command: ::
#
#     zdm gate delete gate_id
#
# where :samp:`gate_id` is the uid of the gate.
#
#     """
#     res = zcli.zdm.gates.delete(gate_id)
#     if res is not None:
#         info("Gate ", gate_id, " succesfully deleted.")
