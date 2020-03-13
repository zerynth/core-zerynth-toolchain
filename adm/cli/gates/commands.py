import click
from base.base import log_table, pass_zcli, info


@click.group()
def webhook():
    """Manage the gates"""
    pass



@webhook.command()
@click.argument('name')
@click.argument('url')
@click.argument("token")
@click.argument("period", type=int)
@click.argument('workspace-id')
@click.argument("tag")
@pass_zcli
def start(zcli, name, url, token, period, workspace_id, tag):
    """Start a new webHook"""
    res = zcli.adm.gate_webhook_data_create(name, url, token, period, workspace_id, tag)
    print(res)


@webhook.command()
@click.option('--status', default="active", type=click.Choice(['active', 'disabled']), help="Filter gates by status.")
@click.option('--origin', default="data", type=click.Choice(['data', 'events']), help="Filter gates by origin.")
@click.argument('workspace-id')
@pass_zcli
def all(zcli, workspace_id, origin, status):
    """Get all gates of a workspace"""
    gates = zcli.adm.gate_workspace_all(workspace_id, status, origin)
    table = []
    for gate in gates:
        table.append([gate.Id, gate.Name, gate.Period, gate.Status, gate.last_schedule])
    log_table(table, headers=["ID", "Name", "Period", "Status", "LastSchedule"])

@webhook.command()
@click.argument('gate-id')
@pass_zcli
def get(zcli, gate_id):
    """Get a single gate"""
    gate = zcli.adm.gate_get(gate_id)
    log_table([[gate.Id, gate.Name, gate.Period, gate.Status, gate.last_schedule]], headers=["ID", "Name", "Period", "Status", "LastSchedule"])

@webhook.command()
@click.argument('gate-id')
@pass_zcli
def disable(zcli, gate_id):
    """ Disable a gate"""
    res = zcli.adm.gate_update(gate_id, status="disabled")
    if res is not None:
        info("Gate ", gate_id, " succesfully disabled.")

@webhook.command()
@click.argument('gate-id')
@pass_zcli
def enable(zcli, gate_id):
    """ Disable a gate"""
    res = zcli.adm.gate_update(gate_id, status="active")
    if res is not None:
        info("Gate ", gate_id, " succesfully enabled.")


@webhook.command()
@click.argument('gate-id')
@pass_zcli
def delete(zcli, gate_id):
    """ Disable a gate"""
    res = zcli.adm.gate_delete(gate_id)
    if res is not None:
        info("Gate ", gate_id, " succesfully deleted.")
