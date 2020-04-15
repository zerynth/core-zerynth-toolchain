"""
.. _zdm-cmd-fota:


Fota
====

The ZDM allows you to enable FOTA (over the air firmware updates) on your devices.

List of FOTA commands:

* :ref:`Upload a firmware <zdm-cmd-fota-prepare>`
* :ref:`Start a FOTA <zdm-cmd-fota-schedule>`
* :ref:`Check FOTA status <zdm-cmd-fota-check>`

    """

import click
from zdevicemanager.base.base import info, log_table, fatal, pass_zcli
from zdevicemanager.base.fs import fs
from zdevicemanager.base.tools import tools

from ..helper import handle_error


@click.group(help="Manage the FOTA update")
def fota():
    pass


@fota.command(help="Upload a firmware to the ZDM")
@click.argument('workspace-id')
@click.argument('files', nargs=-1, type=click.Path(True))
@click.argument('version')
@click.argument("vm-uid")
@pass_zcli
@handle_error
def prepare(zcli, workspace_id, files, version, vm_uid):
    """
    .. _zdm-cmd-fota-prepare:

    Upload a Firmware
    -----------------

    The first step to start a FOTA is to upload a new firmware to the ZDM.
    At first, you have to compile your file: ::

        ztc compile-o fw.c [Firmware project path] target

    where target is the target device, for example "esp32_devkitc"

    Then link the firmware for the bytecode slot 0 ::

        ztc link --bc 0 --file fw0.bin  [VMUID]  fw.c.vbo

    and bytecode slot 1 ::

        ztc link --bc 1 --file fw1.bin  [VMUID]  fw.c.vbo

    Now, use the zdm prepare command to upload your firmware in ZDM.
    Each firmware belongs to a workspace, and it’s identified by the couple <workspaceId, version>. ::

        zdm fota prepare [WorkspaceId] [Files] [Version] [VMUID]

    You can get your Virtual Machine UID using the command: ::

        ztc vm list

        """
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

    res = zcli.zdm.firmwares.upload(workspace_id, version, files, metadata)
    log_table([[res.id, res.version, res.metadata]], headers=["ID", "Version", "Metadata"])


@fota.command(help="Start a fota")
@click.argument('firmware-version')
@click.argument('devices', nargs=-1)
@pass_zcli
@handle_error
def schedule(zcli, firmware_version, devices):
    """
    .. _zdm-cmd-fota-schedule:

    Start a FOTA
    -----------------

    Once you’ve uploaded your firmware, you can send the FOTA command to a device that will download it from the ZDM and uplink it.
    If the FOTA operation is finished, you can see if the device has accepted or refused it using the :ref:`check fota status<zdm-cmd-fota-check>` command.

    To start a fota, type the command: ::

        zdm fota schedule fw_version device_id

    where :samp:`fw_version` is the firmware version associated to the device's workspace uid and :samp:`device_id` is the device you want to send the command to.

        """
    zcli.zdm.fota.schedule(firmware_version, devices)
    info("Sent Fota to devices {}. Firmware Version [{}] ".format(devices, firmware_version))


@fota.command(help="Check the status of a FOTA update on a single device")
@click.argument('device-id')
@pass_zcli
@handle_error
def check(zcli, device_id):
    """
    .. _zdm-cmd-fota-check:

    Check FOTA status
    -----------------

    To check the status of a FOTA you started, to know if the device finished the task or if an error occurred, type the
    following command: ::

        zdm fota check device_uid

    where :samp:`device_uid` is the uid of the device you want to check.

        """
    fota_exp = zcli.zdm.fota.status_expected(device_id)
    fota_cur = zcli.zdm.fota.status_current(device_id)

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
