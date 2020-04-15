"""
.. _zdm-cmd-gates:


Webhooks
========

Using the ZDM you’re able to receive your device’s data on your webhooks.
You can activate a webhook to receive all the data sent on a specific tag in a workspace.
ZDM allows you also to visualize data on Ubidots through a Webhook.


List of commands:

* :ref:`Create <zdm-cmd-webhook-start>`
* :ref:`List webhooks <zdm-cmd-webhook-get-all>`
* :ref:`Get a single webhook <zdm-cmd-webhook-get-webhook>`
* :ref:`Delete a webhook <zdm-cmd-webhook-delete>`
* :ref:`Disable a webhook <zdm-cmd-webhook-disable>`
* :ref:`Enable a webhook <zdm-cmd-webhook-enable>`


    """

import click
from zdevicemanager.base.base import log_table, pass_zcli, info, log_json
from zdevicemanager.base.cfg import env
from ..helper import handle_error


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
@click.option('--origin', type=click.Choice(['data', 'events']), help="The source for webhook (data or events)")
@pass_zcli
@handle_error
def start(zcli, name, url, token, period, workspace_id, tag, fleet, origin="data"):
    """
.. _zdm-cmd-webhook-start:

Webhook creation
----------------

To create a new webhook use the command: ::

    zdm webhook start name url token period workspace_id

where :samp:`name` is the name that you want to give to your new webhook
:samp:`url` is the your webhook
:samp:`token` is the authentication token for your webhook (if needed)

:samp:`workspace_id` is the uid of the workspace you want to receive data from

You also have the possibility to add filters on data using the following options:

:option:`--tag` To specify a tag to filter data (you can specify more than one)
:option:`--fleet` To specify a fleet to filter data (you can specify more than one)
:option:`--token` Token used as value of the Authorization Bearer fot the webhook endpoint.
:option:`--origin` Webhook source (data or events) by default is data.

    """
    tags = []
    fleets = []

    for t in tag:
        tags.append(t)

    for f in fleet:
        fleets.append(f)

    gate_id = zcli.zdm.gates.create_webhook(name, url, token, period, workspace_id, tags, fleets, origin)
    info("Webhook [{}] created succesfully.".format(gate_id))


@webhook.command(help="Get all the webhooks of a workspace")
@click.option('--status', default="active", type=click.Choice(['active', 'disabled']), help="Filter gates by status.")
@click.option('--origin', default=None, type=click.Choice(['data', 'events']), help="Filter gates by origin.")
@click.argument('workspace-id')
@pass_zcli
@handle_error
def all(zcli, workspace_id, origin, status):
    """
.. _zdm-cmd-webhook-get-all:

List webhooks
-------------

To see a list of your webhooks use the command: ::

    zdm webhook all workspace_id

where :samp:`workspace_id` is the uid of the workspace you want to receive data from.

You also have the possibility to add filters on data using the following options:

* :option:`--status active|disabled` to filter on webhook status
* :option:`--origin data` to filter on data origin (data)

    """
    gates = zcli.zdm.gates.list(workspace_id, status, origin)
    table = []

    if env.human:
        for gate in gates:
            table.append([gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled])
        log_table(table, headers=["ID", "Name", "Period", "Status", "LastSchedule"])

    else:
        log_json([gate.toJson for gate in gates])



@webhook.command(help="Get a single webhook")
@click.argument('webhook-id')
@pass_zcli
@handle_error
def get(zcli, webhook_id):
    """
.. _zdm-cmd-webhook-get-webhook:

Get a webhook
-------------

To see information about a single webhook use the command: ::

    zdm webhook get webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    """
    gate = zcli.zdm.gates.get_webhook(webhook_id)
    log_table([[gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled]],
              headers=["ID", "Name", "Period", "Status", "LastSchedule"])


@webhook.command(help="Disable a webhook by its uid")
@click.argument('gate-id')
@pass_zcli
@handle_error
def disable(zcli, gate_id):
    """
.. _zdm-cmd-webhook-disable:

Disable a webhook
-----------------

To disable a webhook use the command: ::

    zdm webhook disable webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    """
    res = zcli.zdm.gates.update_webhook(gate_id, status="disabled")
    if res is not None:
        info("Gate ", gate_id, " succesfully disabled.")


@webhook.command(help="Enable a webhook by its uid")
@click.argument('gate-id')
@pass_zcli
@handle_error
def enable(zcli, gate_id):
    """
.. _zdm-cmd-webhook-enable:

Enable a webhook
-----------------

To enable a webhook use the command: ::

    zdm webhook enable webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    """
    res = zcli.zdm.gates.update_webhook(gate_id, status="active")
    if res is not None:
        info("Gate ", gate_id, " succesfully enabled.")


@webhook.command(help="Delete a webhook")
@click.argument('gate-id')
@pass_zcli
@handle_error
def delete(zcli, gate_id):
    """
.. _zdm-cmd-webhook-delete:

Delete a webhook
-----------------

To delete a webhook use the command: ::

    zdm webhook delete webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    """
    res = zcli.zdm.gates.delete_webhook(gate_id)
    if res is not None:
        info("Gate ", gate_id, " succesfully deleted.")
