from zdevicemanager.base import cli

from .device.commands import device
from .fleet.commands import fleet
from .job.commands import job
from .fota.commands import fota
from .workspace.commands import workspace
from .gates.commands import gate
from .gates.webhooks.commands import webhook
from .gates.dump.commands import export as exportgate
from .gates.alarm.commands import alarm
from .auth.commands import login, logout
from .workspace.conditions.commands import condition
from .workspace.data.commands import data
from .workspace.data.export.commands import export

# Account commmands
cli.add_command(login)
cli.add_command(logout)

# workspace comands
data.add_command(export)
workspace.add_command(condition)
workspace.add_command(data)
cli.add_command(workspace)

cli.add_command(device)
cli.add_command(fleet)

# gates commands
cli.add_command(gate)
gate.add_command(webhook)
gate.add_command(exportgate)
gate.add_command(alarm)

#job
cli.add_command(job)

# fota
cli.add_command(fota)

