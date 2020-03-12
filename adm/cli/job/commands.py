import click

from base.base import info, pass_zcli


@click.group()
def job():
    """Manage the jobs sent to the device"""
    pass


@job.command()
@click.argument('name')
@click.argument('args')  # json = { }
@click.argument('devices', nargs=-1, type=click.STRING)
@pass_zcli
def start(zcli, key, value, targets):
    """Send a Job """
    # add a "@" to the name of the job
    pass
    # id = zcli.adm._create_changeset(key, value, targets)
    # info("Created Job", id)


@job.command()
@click.argument('name')
@click.argument('device')
@pass_zcli
def status(zcli, name, device):
    """Send a Job """
    pass
    # id = zcli.adm._create_changeset(key, value, targets)
    # info("Created Job", id)
