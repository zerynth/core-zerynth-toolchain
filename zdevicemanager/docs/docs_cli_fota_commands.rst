.. _zdm-cmd-fota:


Fota
====

The ZDM allows you to enable FOTA (over the air firmware updates) on your devices.

List of FOTA commands:

* :ref:`Upload a firmware <zdm-cmd-fota-prepare>`
* :ref:`Start a FOTA <zdm-cmd-fota-schedule>`
* :ref:`Check FOTA status <zdm-cmd-fota-check>`

    
.. _zdm-cmd-fota-prepare:

Prepare the FOTA
-----------------

The command compiles and uploads the firmware for a device into ZDM.
The version is a string identifying the version of the firmware (e.g., "1.0"). ::

    zdm fota prepare [Firmware project path] [DeviceId] [Version]
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

    
