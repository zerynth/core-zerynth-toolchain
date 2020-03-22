import click
from base.base import info, log_table, fatal, pass_zcli
from base.fs import fs
from base.tools import tools

from ..helper import handle_error


@click.group()
def fota():
    """Manage the fota"""
    pass


# ZTC="$PY $ZDIR/ztc/ztc.py"
# VMUID="tPDTgFApRJmUdyf2PHBqKw"
## CHANGE THIS TO THE CORRECT VM UID

# # compile project
# $ZTC compile .. juul_f429zi -o bytecode.vbo
# # link project
# $ZTC link $VMUID bytecode.vbo --bc 1 --file bc.bin --bin

@fota.command()
@click.argument('workspace-id')
@click.argument('files', nargs=-1, type=click.Path(True))
@click.argument('version')
@click.argument("vm-uid")
@pass_zcli
@handle_error
def prepare(zcli, workspace_id, files, version, vm_uid):
    """Upload the firmwares for the FOTA."""
    # file bin di prova = /home/davide/test-esp32/main.vbo
    filevm = tools.get_vm_by_uid(vm_uid)
    if not filevm or not fs.exists(filevm):
        fatal("Can't find vm", vm_uid)
    j = fs.get_json(filevm)
    if 'hash_features' not in j:
        fatal("Can't find hash feature of vm", vm_uid)
    vm_hash_featues = j['hash_features']
    if 'version' not in j:
        fatal("Can't find the version of vm", vm_uid)
    vm_version = j['version']

    metadata = {"vm_version": vm_version, "vm_feature": vm_hash_featues}

    res = zcli.adm.firmwares.upload(workspace_id, version, files, metadata)
    log_table([[res.id, res.version, res.metadata]], headers=["ID", "Version", "Metadata"])


@fota.command()
@click.argument('firmware-version')
@click.argument('devices', nargs=-1)
# @click.command("on-time")
@pass_zcli
@handle_error
def schedule(zcli, firmware_version, devices):
    """Start a fota"""
    zcli.adm.fota.schedule(firmware_version, devices)
    info("Sent Fota to devices {}. Firmware Version [{}] ".format(devices, firmware_version))


@fota.command()
@click.argument('device-id')
@pass_zcli
@handle_error
def check(zcli, device_id):
    """Check the status of a fota on a single device."""

    fota_exp = zcli.adm.fota.status_expected(device_id)
    fota_cur = zcli.adm.fota.status_current(device_id)

    schedule_at = fota_exp.version if fota_exp else "<none>"

    if fota_exp is None and fota_cur is not None:
        # the job has been scheduled (exp is None)  and the device has sent the response (fota_cur not None)
        status = "done"
    elif fota_exp is None and fota_cur is None:
        # the job has not been scheduled nor a response has been received
        status = "<none>"
    elif fota_exp is not None and fota_cur is not None:
        # job has been scheduled and the device has sent a response
        status = "done"
    elif fota_exp is not None and fota_cur is None:
        # the job has been scheduled bu the device has not sent a response
        status = "pending"
    else:
        status = "<unknown>"

    if fota_cur is not None:
        status = fota_cur.status

    result = fota_cur.value if fota_cur is not None else "<no result>"
    result_at = fota_cur.version if fota_cur is not None else "<no result>"

    log_table([[ status, schedule_at, result, result_at, ]],
              headers=[ "Status", "ScheduleAt", "Result", "ResultAt"])
