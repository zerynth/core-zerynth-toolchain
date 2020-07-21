"""
.. _zdm-cmd-gates-webhook:


Webhook gates
============

List of commands:

* :ref:`Create webhook <zdm-cmd-gates-webhook-create>`
* :ref:`Update webhook <zdm-cmd-gates-webhook-update>`
* :ref:`List webhooks <zdm-cmd-gates-webhook-get-all>`

    """

import click
from zdevicemanager.cli.helper import handle_error
from zdevicemanager.base.cfg import env
from zdevicemanager.base.base import log_table, pass_zcli, info, log_json


@click.group(help="Manage the webhooks")
def webhook():
    pass


@webhook.command(help="Create a new webhook")
@click.argument('name')
@click.argument('url')
@click.argument("period", type=int)
@click.argument('workspace-id')
@click.option('--tag', multiple=True)
@click.option('--fleet', multiple=True)
@click.option('--token', default="", help="Token used as value of the Authorization Bearer of the webhook endpoint.")
@pass_zcli
@handle_error
def create(zcli, name, url, token, period, workspace_id, tag, fleet, origin="data"):
    """
.. _zdm-cmd-gates-webhook-create:

Webhook creation
----------------

To create a new webhook use the command: ::

    zdm gate webhook create name url token period workspace_id

where :samp:`name` is the name of the webhook
:samp:`url` is the webhook url
:samp:`token` is the authentication token for the webhook (if needed)

:samp:`workspace_id` is the uid of the workspace

It's also possible to to add filters on data using the following options:

:option:`--tag` To specify a tag to filter data (one or more)
:option:`--fleet` To specify a fleet to filter data (one or more)
:option:`--token` Token used as value of the Authorization Bearer fot the webhook endpoint.

    """
    tags = []
    fleets = []

    for t in tag:
        tags.append(t)

    for f in fleet:
        fleets.append(f)

    gate_id = zcli.zdm.webhooks.create(name, url, token, period, workspace_id, tags, fleets, origin)
    info("Webhook [{}] created succesfully.".format(gate_id))


@webhook.command(help="List all the webhooks")
@click.option('--status', default="active", type=click.Choice(['active', 'disabled']), help="Filter gates by status.")
@click.argument('workspace-id')
@pass_zcli
@handle_error
def all(zcli, workspace_id, status):
    """
.. _zdm-cmd-gates-webhook-get-all:

List export gates
-----------------

To see the list of the webhooks use the command: ::

    zdm gate webhook all workspace_id

where :samp:`workspace_id` is the uid of the workspace

It's also possible to add filters on gates using the following options:

* :option:`--status active|disabled` to filter on gate's status

    """
    gates = zcli.zdm.gates.list(workspace_id, status, 'webhook')
    table = []

    if env.human:
        for gate in gates:
            table.append([gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled])
        log_table(table, headers=["ID", "Name", "Period", "Status", "LastSchedule"])

    else:
        log_json([gate.toJson for gate in gates])


@webhook.command(help="Update an webhook gate")
@click.argument('gate-id')
@click.option('--name', help='To change webhook name')
@click.option('--period', help='To change webhook period', type=int)
@click.option('--url', help='To change webhook url')
@click.option('--tokens', help='To change webhook tokens')
@click.option('--tags', multiple=True, help='To replace gate tags')
@click.option('--fleets', multiple=True, help='To replace gate fleets')
@pass_zcli
@handle_error
def update(zcli, gate_id, name=None, period=None, url=None, tokens=None, tags=None, fleets=None):

    """
.. _zdm-cmd-gates-webhook-update

Update webhook
--------------

To update a webhook use the command: ::

    zdm gate webhook update gate_id

To change gate's configuration use the following options: ::
* :option:`--name` to change the webhook name
* :option:`--period` to change the webhook period
* :option:`--url` to change the webhook url
* :option:`--tag` (multiple option) to replace webhook tag array
* :option:`--fleet` (multiple option) to replace webhook fleets array

    """
    zcli.zdm.webhooks.update(gate_id, name, period, url, tokens, tags, fleets)
    info("Gate [{}] updated correctly.".format(gate_id))
