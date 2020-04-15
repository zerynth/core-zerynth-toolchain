from zdevicemanager.base import cli

from .device.commands import device
from .fleet.commands import fleet
from .job.commands import job
from .fota.commands import fota
from .workspace.commands import workspace
from .events.commands import event
from .gates.commands import webhook
from .auth.commands import login, logout

cli.add_command(login)
cli.add_command(logout)
cli.add_command(job)
cli.add_command(fota)
cli.add_command(webhook)
cli.add_command(workspace)
cli.add_command(device)
cli.add_command(fleet)
cli.add_command(event)
