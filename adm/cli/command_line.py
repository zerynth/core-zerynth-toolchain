from base.base import cli

from .device.commands import device
from .fleet.commands import fleet
from .job.commands import job
from .fota.commands import fota
from .workspace.commands import workspace
from .gates.commands import gate
from user.usercmd import user_login


cli.add_command(job)
cli.add_command(fota)
cli.add_command(gate)
cli.add_command(workspace)
cli.add_command(device)
cli.add_command(fleet)
