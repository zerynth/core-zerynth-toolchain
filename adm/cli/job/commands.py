import click

from base.base import info, pass_zcli, log_table
from ..helper import handle_error

@click.group()
def job():
    """Manage the jobs sent to the devices"""
    pass


@job.command()
@click.argument('name')
@click.argument('devices', nargs=-1, type=click.STRING)
@click.option('--arg', type=(str, str), multiple=True)
@pass_zcli
@handle_error
def schedule(zcli, name, arg, devices):
    """Schedule a Job"""
    # args is a tuple of typle (('temp', 'yes'), ('on', True))
    args_dict = {}
    for a in arg:
        arg_name = a[0]
        arg_value = a[1]
        if check_int(a[1]):
            arg_value = int(a[1])
        args_dict[arg_name] = arg_value
    res = zcli.adm.jobs.schedule(name, args_dict, devices, on_time="")
    print(res)
    info("Job [{}] scheduled correctly.".format(name))

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


@job.command()
@click.argument('name')
@click.argument('device-id', nargs=1, type=click.STRING)
@pass_zcli
@handle_error
def status(zcli, name, device_id):
    """Check the job status sent to a device."""

    status = zcli.adm.jobs.status(name, device_id)
    if status:
         log_table([[status.name, status.value, status.version]],headers=["Name", "Value", "Timestamp"])
    else:
        info("No job [{}] for device [{}].".format(name, device_id))
