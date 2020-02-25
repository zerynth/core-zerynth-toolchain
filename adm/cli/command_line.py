import click
from base.base import cli
from base.cfg import env

from adm.client.admclient import ADMClient
from .device.commands import device
from .fleet.commands import fleet
from .workspace.commands import workspace


@cli.group()
@click.option('--adm-url', envvar='ZERYNTH_ADM_URL', default='http://api.ad.zerinth.com/v1')
@click.pass_context
def adm(ctx, adm_url):
    """Manage the adm"""
    ctx.obj = ADMClient(workspace_url=env.adm.workspaces, device_url=env.adm.devices, fleet_url=env.adm.fleets)

adm.add_command(workspace)
adm.add_command(device)
adm.add_command(fleet)
