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
def check(zcli, name, device_id):
    """Check the job status for a single device."""

    status_exp = zcli.adm.jobs.status_expected(name, device_id)
    status_cur = zcli.adm.jobs.status_current(name, device_id)

    schedule_at = status_exp.version if status_exp else "<none>"

    if status_exp is None and status_cur is not None:
        # the job has been scheduled (exp is None)  and the device has sent the response (status_cur not None)
        status = "done"
    elif status_exp is None and status_cur is None:
        # the job has not been scheduled nor a response has been received
        status = "<none>"
    elif status_exp is not None and status_cur is not None:
        # job has been scheduled and the device has sent a response
        status = "done"
    elif status_exp is not None and status_cur is None:
        # the job has been scheduled bu the device has not sent a response
        status = "pending"
    else:
        status = "<unknown>"

    if status_cur is not None:
        status = status_cur.status

    result = status_cur.value if status_cur is not None else "<no result>"
    result_at = status_cur.version if status_cur is not None else "<no result>"

    log_table([[name, status, schedule_at, result, result_at, ]],
              headers=["Name", "Status", "ScheduleAt", "Result", "ResultAt"])
