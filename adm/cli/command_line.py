import click
from adm.client.admclient import ADMClient
from base.base import cli
from base.cfg import env
from user import user_login, user_logout

from .device.commands import device
from .fleet.commands import fleet
from .status.commands import status
from .workspace.commands import workspace
from .fota.commands import fota


@cli.group()
# @click.option('--adm-url', envvar='ZERYNTH_ADM_URL', default='http://api.adm.zerinth.com/v1')
@click.pass_context
def adm(ctx):
    """Manage the adm"""
    ctx.obj = ADMClient(workspace_url=env.adm.workspaces, device_url=env.adm.devices, fleet_url=env.adm.fleets,
                        status_url=env.adm.status)

@adm.command()
@click.option("--token", default=None, help="set the token in non interactive mode")
@click.option("--user", default=None, help="username for manual login")
@click.option("--passwd", default=None, help="password for manual login")
@click.option("--origin", default=None, help="origin for 3dparty auth")
@click.option("--origin_username", default=None, help="origin username for 3dparty auth")
def login(token, user, passwd, origin, origin_username):
    user_login(token, user, passwd, origin, origin_username)


@adm.command("logout", help="Close current session. A new login is needed")
def logout():
    user_logout

adm.add_command(workspace)
adm.add_command(fota)
adm.add_command(device)
adm.add_command(fleet)
adm.add_command(status)
