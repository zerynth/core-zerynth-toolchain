import click
from base.base import log_table, pass_zcli, info

from ..helper import handle_error


@click.group()
def webhook():
    """Manage the webHooks gates."""
    pass


@webhook.command()
@click.argument('name')
@click.argument('url')
@click.argument("token")
@click.argument("period", type=int)
@click.argument('workspace-id')
@click.argument("tag")
@pass_zcli
@handle_error
def start(zcli, name, url, token, period, workspace_id, tag):
    """Start a new webHook"""
    gate_id = zcli.adm.gates.create_webhook(name, url, token, period, workspace_id, tag)
    info("Web hook [{}] created succesfully.".format(gate_id))


@webhook.command()
@click.option('--status', default="active", type=click.Choice(['active', 'disabled']), help="Filter gates by status.")
@click.option('--origin', default="data", type=click.Choice(['data', 'events']), help="Filter gates by origin.")
@click.argument('workspace-id')
@pass_zcli
@handle_error
def all(zcli, workspace_id, origin, status):
    """Get all webhook of a workspace"""
    gates = zcli.adm.gates.list(workspace_id, status, origin)
    table = []
    for gate in gates:
        table.append([gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled])
    log_table(table, headers=["ID", "Name", "Period", "Status", "LastSchedule"])


@webhook.command()
@click.argument('gate-id')
@pass_zcli
@handle_error
def get(zcli, gate_id):
    """Get a single webhook"""
    gate = zcli.adm.gates.get_webhook(gate_id)
    log_table([[gate.id, gate.name, gate.period, gate.status, gate.last_time_scheduled]],
              headers=["ID", "Name", "Period", "Status", "LastSchedule"])


@webhook.command()
@click.argument('gate-id')
@pass_zcli
@handle_error
def disable(zcli, gate_id):
    """ Disable a webhook"""
    res = zcli.adm.gates.update_webhook(gate_id, status="disabled")
    if res is not None:
        info("Gate ", gate_id, " succesfully disabled.")


@webhook.command()
@click.argument('gate-id')
@pass_zcli
@handle_error
def enable(zcli, gate_id):
    """ Enable a webhook"""
    res = zcli.adm.gates.update_webhook(gate_id, status="active")
    if res is not None:
        info("Gate ", gate_id, " succesfully enabled.")


@webhook.command()
@click.argument('gate-id')
@pass_zcli
@handle_error
def delete(zcli, gate_id):
    """ Delete a webhook"""
    res = zcli.adm.gates.delete_webhook(gate_id)
    if res is not None:
        info("Gate ", gate_id, " succesfully deleted.")
