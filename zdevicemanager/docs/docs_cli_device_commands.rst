.. _zdm-cmd-device:


Devices
=======

In the ZDM a device is a peripheral that can execute Zerynth bytecode. In order to do so a device must be prepared and customized with certain attributes.
The main attributes of a device are:

* :samp:`uid` a unique id provided by the ZDM with the :ref:`device creation <zdm-cmd-device-create>` command
* :samp:`name` a name given by the user to the device in order to identify it

1. The first step to connect your device to the ZDM, once you are logged, is the device :ref:`creation <zdm-cmd-device-create>`.
2. Then you have to :ref:`create a key <zdm-cmd-device-create-key>` and :ref:`generate a jwt<zdm-cmd-device-generate-jwt>`.

There also are commands to :ref:`list your devices <zdm-cmd-device-get-all>`, to :ref:`get a single device info <zdm-cmd-device-get-device>`,
:ref:`update a device <zdm-cmd-device-update>` and to :ref:`list all device's key <zdm-cmd-device-get-all-keys>`


List of device commands:

* :ref:`Create <zdm-cmd-device-create>`
* :ref:`List devices <zdm-cmd-device-get-all>`
* :ref:`Get a single device <zdm-cmd-device-get-device>`
* :ref:`Create a device's key <zdm-cmd-device-create-key>`
* :ref:`List a device's keys <zdm-cmd-device-get-all-keys>`
* :ref:`Generate a password from a key <zdm-cmd-device-generate-jwt>`


The list of supported devices is available :ref:`here <doc-supported-boards>`

    
.. _zdm-cmd-device-create:

Device creation
---------------

To connect your device to the ZDM you must first create a new device on ZDM, to obtain a new device uid.
The creation command is: ::

    zdm device create name

where :samp:`name` is the name that you want to give to your new device

If you create your device using this command, it will be associated to your default fleet inside your default workspace.
If you want, you can choose to associate the device to another fleet with the optional argument:

:option:`--fleet-id uid`

If you want to associate the device to another fleet, see the :ref:`update command <zdm-cmd-device-update>`
    
.. _zdm-cmd-device-get-all:

List devices
------------

If you want to list all your devices, you can use this command to see a table with a device for each rows and 4 columns containing the device uid, name and the uid of the fleet and workspace containing them
to see all your devices use the command: ::

    zdm device all

    
.. _zdm-cmd-device-get-device:

Get device
----------

To get a single device information, you can use this command to see the device name and the uid of the fleet and the workspace that contain it. ::

    zdm device get uid

where :samp:`uid` is the device uid.

    
.. _zdm-cmd-device-update:

Update a device
---------------

Once you've created a device, you can use this command to update the device name, or to change the fleet uid associated to.
To update a device you just need its uid as argument, then you can use optional arguments to update its name or fleet uid.
Use the command: ::

    zdm device update uid

And the optional arguments are:

* :option:`--fleet-id uid` the uid of the fleet you want to associate the device to
* :option:`--name name` the name you want to give to the device

    
.. _zdm-cmd-device-create-key:

Create a key
------------

To be able to connect your device to the ZDM you must create a key at first and then generate a password (as jwt token) from the created key.
You can generate different keys with different names for your devices with the command: ::

    zdm device key create uid name

Where :samp:`uid` is the device uid and :samp:`name` is the name you want to give to the key.
This command returns the generated key information as the key id, the name, the creation date and if the key has been revoked or not.

To connect your device to the ZDM, there is one last step to follow: :ref:`jwt generation <zdm-cmd-device-generate-jwt>`


    
.. _zdm-cmd-device-generate-jwt:

Generate a device's password (jwt)
---------------------------------

To be able to connect your device to the ZDM you must create a key at first and then generate a password (as jwt token) from the created key.
You can generate different keys with different names for your devices with the command: ::

    zdm device key create uid name

Where :samp:`uid` is the device uid and :samp:`name` is the name you want to give to the key
This command returns the generated key information as the key id, the name, the creation date and if the key has been revoked or not.

    
.. _zdm-cmd-device-get-all-keys:

List device keys
----------------

To see all the keys you have created for a device, use the command: ::

    zdm device key all uid

Where :samp:`uid` is the device uid.

This command returns for each key the id, the name, the creation date and if it's or not revoked.

    
