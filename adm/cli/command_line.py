from base.base import cli

from .device.commands import device
from .fleet.commands import fleet
from .job.commands import job
from .fota.commands import fota
from .workspace.commands import workspace
from .gates.commands import gate
from user.usercmd import user_login

# @cli.command()
# @click.option("--token", default=None, help="set the token in non interactive mode")
# @click.option("--user", default=None, help="username for manual login")
# @click.option("--passwd", default=None, help="password for manual login")
# @click.option("--origin", default=None, help="origin for 3dparty auth")
# @click.option("--origin_username", default=None, help="origin username for 3dparty auth")
# def login(token, user, passwd, origin, origin_username):
#     user_login(token, user, passwd, origin, origin_username)
#
#
# @cli.command("logout", help="Close current session. A new login is needed")
# def logout():
#     user_logout


cli.add_command(job)
cli.add_command(fota)
cli.add_command(gate)
cli.add_command(workspace)
cli.add_command(device)
cli.add_command(fleet)
