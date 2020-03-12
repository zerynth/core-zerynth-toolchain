import click
from base.base import info, log_table, fatal, pass_zcli


@click.group()
def gate():
    """Manage the gates"""
    pass


@gate.command()
@click.argument('name')
@click.argument('url')
@click.argument("token")
@click.argument("period")
@click.argument('workspace-id')
@click.argument("tag")
@pass_zcli
def prepare(zcli, name, files, version, vm_uid):
    pass

@gate.command()
@click.argument('firmware-version')
@click.argument('devices', nargs=-1)
@pass_zcli
def schedule(zcli, firmware_version, devices):
    """Start a fota"""
    pass

