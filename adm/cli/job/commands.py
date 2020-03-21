import click

from base.base import info, pass_zcli, log_table
from adm.client.helper import convert_into_job, from_job_name


@click.group()
def job():
    """Manage the jobs sent to the devices"""
    pass


@job.command()
@click.argument('name')
@click.option('--arg', type=(str, str), multiple=True)
@click.argument('devices', nargs=-1, type=click.STRING)
@pass_zcli
def schedule(zcli, name, arg, devices):
    """Send a Job """
    # add a "@" to the name of the job
    # args is a nttyple of typle (('er', 's'), ('caio', '23'))
    args_dict = {}
    for a in arg:
        arg_name = a[0]
        arg_value = a[1]
        if check_int(a[1]):
            arg_value = int(a[1])
        args_dict[arg_name] = arg_value
    res = zcli.adm.job_schedule(name, args_dict, devices, on_time="")

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


@job.command()
@click.argument('name')
@click.argument('device', nargs=1, type=click.STRING)
@pass_zcli
def status(zcli, name, device):
    """Check the jo result of a device"""
    status = zcli.adm._get_current_device_status(device)
    result = list(filter(lambda x: x.name == convert_into_job(name), status))
    table = []
    if len(result) > 0:
        res = result[0]
        table.append([from_job_name(res.name), res.Value, res.Timestamp])
    log_table(table, headers=["Name", "Result", "Time"])
