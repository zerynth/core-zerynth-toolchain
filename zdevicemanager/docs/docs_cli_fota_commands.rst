.. _zdm-cmd-fota:


Fota
====

The ZDM allows you to enable FOTA (over the air firmware updates) on your devices.

List of FOTA commands:

* :ref:`Upload a firmware <zdm-cmd-fota-prepare>`
* :ref:`Start a FOTA <zdm-cmd-fota-schedule>`
* :ref:`Check FOTA status <zdm-cmd-fota-check>`

    
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

    
.. _zdm-cmd-fota-schedule:

Start a FOTA
-----------------

Once you’ve uploaded your firmware, you can send the FOTA command to a device that will download it from the ZDM and uplink it.
If the FOTA operation is finished, you can see if the device has accepted or refused it using the :ref:`check fota status<zdm-cmd-fota-check>` command.

To start a fota, type the command: ::

    zdm fota schedule fw_version device_id

where :samp:`fw_version` is the firmware version associated to the device's workspace uid and :samp:`device_id` is the device you want to send the command to.

    
.. _zdm-cmd-fota-check:

Check FOTA status
-----------------

To check the status of a FOTA you started, to know if the device finished the task or if an error occurred, type the
following command: ::

    zdm fota check device_uid

where :samp:`device_uid` is the uid of the device you want to check.

    
