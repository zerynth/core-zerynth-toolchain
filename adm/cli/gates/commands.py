import click
from base.base import pass_zcli


@click.group()
def gate():
    """Manage the gates"""
    pass


@gate.command()
@click.argument('name')
@click.argument('url')
@click.argument("token")
@click.argument("period", type=int)
@click.argument('workspace-id')
@click.argument("tag")
@pass_zcli
def start(zcli, name, url, token, period, workspace_id, tag):
    res = zcli.adm.gate_webhook_data_create(name,url, token, period, workspace_id, tag)
    print(res)

@gate.command()
@click.argument('gate-id')
@pass_zcli
def get(zcli, gate_id):
    """Get a single gate"""
    pass
