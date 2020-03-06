import click
from base.base import info, log_table, fatal
from base.fs import fs
from base.tools import tools

from ..helper import pass_adm


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
# @click.argument('file', type=click.Path(exists=True))
@click.argument('files', nargs=-1, type=click.Path(True))
@click.argument('version')
@click.argument("vm-uid")
@pass_adm
def prepare(adm, workspace_id, files, version, vm_uid):
    """Prepare the FOTA uploading the firmware"""
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
    # TODO: add a list of binaries in base64 instead of one binary.
    res = adm.firmware_upload(workspace_id, files, version, metadata)
    info("Uploaded firmware " + res.Id)


@fota.command()
@click.argument('workspace-id')
@pass_adm
def all(adm, workspace_id):
    """Get all the firmware of a workspace"""
    table = []
    firmwares = adm.firmware_all(workspace_id)
    for d in firmwares:
        table.append([d.Id, d.Version, d.WorkspaceID if d.WorkspaceID else "<none>"])
    log_table(table, headers=["ID", "Version", "WorkspaceID"])


@fota.command()
@click.argument('firmware-version')
@click.argument('devices', nargs=-1)
# @click.command("on-time")
@pass_adm
def schedule(adm, firmware_version, devices):
    """Start a fota"""
    devs = [d for d in devices]
    res = adm.fota_schedule(firmware_version, devs)
    info("Sent fota to devices ", devs)


@fota.command()
@click.argument('devices', nargs=-1)
@pass_adm
def check(adm, devices):
    """Check the status of a fota on multiple devices"""
    table = []
    for dmsg in adm.fota_check(devices):
        table.append([dmsg["device"], dmsg['status']])
    log_table(table, headers=["Device", "Status"])
