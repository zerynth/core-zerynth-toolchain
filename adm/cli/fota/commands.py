import click
from base.base import info, log_table

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
@click.argument('workspace_id')
@click.argument('file', type=click.Path(exists=True))
@click.argument('version')
@click.argument("bc-slot")
@click.argument("vm-slot")
@click.argument("vm-uid")
@pass_adm
def prepare(adm, workspace_id, file, version, bc_slot, vm_slot, vm_uid):
    """Prepare the FOTA uploading the firmware"""
    metadata = {"bc_slot": bc_slot, "vm_slot": vm_slot, "vm_uid": vm_uid}
    res = adm.firmware_upload(workspace_id, file, version, metadata)
    info("Uploaded firmware " + res.Id + "with version " + res.Version)

@fota.command()
@click.argument('workspace_id')
@pass_adm
def all(adm, workspace_id):
    """Get all the firmware of a workspace"""
    table = []
    firmwares = adm.firmware_all(workspace_id)
    print(firmwares)
    for d in firmwares:
        table.append([d.Id, d.Version, d.WorkspaceID if d.WorkspaceID else "<none>"])
    log_table(table, headers=["ID", "Version", "WorkspaceID"])


@fota.command()
@click.argument('firmware_id')
@click.argument('devices', nargs=-1)
#@click.command("on-time")
@pass_adm
def schedule(adm, firmware_id, devices):
    """Start a fota"""

    devs = [d for d in devices]

    res = adm.fota_schedule(firmware_id, devs)
    print(res)

# @fota.command()
# @click.argument('device')
# @click.argument('firmware_id')
# @pass_adm
# def check(adm, device, firmware_id):
#     """Start a fota"""
#     pass
