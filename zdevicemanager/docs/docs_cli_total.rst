##########################
Zerynth Device Manager CLI
##########################

ZDM Command Line Interface (CLI) allows managing the ZDM via command line. The ZDM CLI directly interface with the ZDM API allowing the creation of scripts that goes beyond the simplified ZDM web user interface.

.. _zdm-cmd-auth:


Authentication
==============

The ZDM allows the user to authenticate against the Zerytnh backend.

The following commands are available:

* :ref:`login <zdm-cmd-auth-login>` to retrieve an authentication token.
* :ref:`logout <zdm-cmd-auth-logout>` to delete the current session.
.. _zdm-cmd-auth-login:

Login
-----

The :command:`login` command enables the user to retrieve an authentication token. The token is used in most zdm commands to communicate with the Zerynth backend.

The :command:`login` can be issued in interactive and non interactive mode. Interactive mode is started by typing: ::

    zdm login

The zdm opens the default system browser to the login/registration page and waits for user input.

In the login/registration page, the user can login providing a valid email and the corresponding password.
It is also possible (and faster) to login using Google plus or Facebook OAuth services. If the user do not have a Zerynth account it is possible to register
providing a valid email, a nick name and a password. Social login is also available for registration via OAuth.

Once a correct login/registration is performed, the browser will display an authentication token. Such token can be copied and pasted to the zdm prompt.

.. warning:: multiple logins with different methods (manual or social) are allowed provided that the email linked to the social OAuth service is the same as the one used in the manual login.


Non interactive mode is started by typing: ::

    zdm login --token authentication_token

The :samp:`authentication_token` can be obtained by manually opening the login/registration `page <https://backend.zerynth.com/v1/sso>`_


.. warning:: For manual registrations, email address confirmation is needed. An email will be sent at the provided address with instructions.

    
.. _zdm-cmd-auth-logout:

Logout
------

Delete current session with the following command ::

    zdm logout


.. note:: it will be necessary to login again.

    


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


.. _zdm-cmd-fleet:


Fleets
======

In the ZDM a fleet is a set of devices. When you log in for the first time, a 'default' fleet will be created.
The main attributes of a fleet are:

* :samp:`uid`, a unique id provided by the ZDM after the :ref:`fleet creation <zdm-cmd-fleet-create>` command
* :samp:`name`, a name given by the user to the fleet in order to identify it


List of fleet commands:

* :ref:`Create <zdm-cmd-fleet-create>`
* :ref:`List fleets <zdm-cmd-fleet-get-all>`
* :ref:`Get a single fleet <zdm-cmd-fleet-get-fleet>`

    
.. _zdm-cmd-fleet-create:

Fleet creation
--------------

To create a new fleet of devices inside a workspace use the command: ::

    zdm fleet create name workspace_uid

where :samp:`name` is the name you want to give to your new fleet and :samp:`workspace_id` is the uid of the workspace that will contain the fleet.

    
.. _zdm-cmd-fleet-get-all:

List fleets
------------

If you want to list all your fleets, you can use this command to have information about the associated workspace, and the list of devices inside: ::

    zdm fleet all

    
.. _zdm-cmd-fleet-get-fleet:

Get fleet
---------

To get a single fleet information, you can use this command to see its name, the uid of the workspace that contains it and the list of devices inside::

    zdm fleet get uid

where :samp:`uid` is the fleet uid

    
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

    
.. _zdm-cmd-gates:


Webhooks
========

Using the ZDM you’re able to receive your device’s data on your webhooks.
You can activate a webhook to receive all the data sent on a specific tag in a workspace.
ZDM allows you also to visualize data on Ubidots through a Webhook.


List of commands:

* :ref:`Create <zdm-cmd-webhook-start>`
* :ref:`List webhooks <zdm-cmd-webhook-get-all>`
* :ref:`Get a single webhook <zdm-cmd-webhook-get-webhook>`
* :ref:`Delete a webhook <zdm-cmd-webhook-delete>`
* :ref:`Disable a webhook <zdm-cmd-webhook-disable>`
* :ref:`Enable a webhook <zdm-cmd-webhook-enable>`


    
.. _zdm-cmd-webhook-start:

Webhook creation
----------------

To create a new webhook use the command: ::

    zdm webhook start name url token period workspace_id tag

where :samp:`name` is the name that you want to give to your new webhook
:samp:`url` is the your webhook
:samp:`token` is the authentication token for your webhook (if needed)

:samp:`workspace_id` is the uid of the workspace you want to receive data from
:samp:`tag` is the tag of the data you want to receive

You also have the possibility to add filters on data using the following options:

:option:`--token` Token used as value of the Authorization Bearer fot the webhook endpoint.
    
.. _zdm-cmd-webhook-get-all:

List webhooks
-------------

To see a list of your webhooks use the command: ::

    zdm webhook all workspace_id

where :samp:`workspace_id` is the uid of the workspace you want to receive data from.

You also have the possibility to add filters on data using the following options:

* :option:`--status active|disabled` to filter on webhook status
* :option:`--origin data` to filter on data origin (data)

    
.. _zdm-cmd-webhook-get-webhook:

Get a webhook
-------------

To see information about a single webhook use the command: ::

    zdm webhook get webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
.. _zdm-cmd-webhook-disable:

Disable a webhook
-----------------

To disable a webhook use the command: ::

    zdm webhook disable webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
.. _zdm-cmd-webhook-enable:

Enable a webhook
-----------------

To enable a webhook use the command: ::

    zdm webhook enable webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
.. _zdm-cmd-webhook-delete:

Delete a webhook
-----------------

To delete a webhook use the command: ::

    zdm webhook delete webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
.. _zdm-cmd-job:


Jobs
====

In the ZDM a job is a function defined in your firmware that you can call remotely through the ZDM.
There are to operations available in the ZDM for jobs:


List of device commands:

* :ref:`Schedule <zdm-cmd-job-schedule>`
* :ref:`Check a job status <zdm-cmd-job-check>`

    
.. _zdm-cmd-job-schedule:

Schedule a job
---------------

In the ZDM will be soon available to schedule jobs in time, At the moment, it's only possible to send it immediately to a device.
To call remotely a function defined in your firmware, use the command: ::

    zdm job schedule job uid

where :samp:`job` is the function name and :samp:`uid` is the device uid.

If your function expects parameters to work, you can use the command option :option:`--arg`

    
.. _zdm-cmd-job-check:

Check a job status
------------------

If you want to check the status of a job you scheduled, type the command: ::

    zdm job check job uid

where :samp:`job` is the job name and :samp:`uid` is the device uid you want to check, you will see if your device sent a response to the job.

    
.. _zdm-cmd-workspace:

Workspaces
==========

In the ZDM a workspace is the root node in Zerynth device management. A workspace represents a project containing fleets of devices.
The main attributes of a workspace are:

* :samp:`uid` a unique id provided by the ZDM with the :ref:`workspace creation <zdm-cmd-workspace-create>` command
* :samp:`name` a name given by the user to the workspace in order to identify it
* :samp:`description` a string given by the user to describe the project

At your first log in, a 'default' workspace containing a 'default' fleet will be created.


List of device commands:

* :ref:`Create <zdm-cmd-workspace-create>`
* :ref:`List workspaces <zdm-cmd-workspace-get-all>`
* :ref:`Get a single workspace <zdm-cmd-workspace-get-workspace>`
* :ref:`Get data <zdm-cmd-workspace-data>`
* :ref:`List firmwares <zdm-cmd-workspace-firmware>`
* :ref:`List workspace tags <zdm-cmd-workspace-tag>`


The list of supported devices is available :ref:`here <doc-supported-boards>`

    
.. _zdm-cmd-workspace-get-all:

List workspaces
---------------

To see the list of all your workspaces, use the command: ::

    zdm workspace all

    
.. _zdm-cmd-workspace-get-workspace:

Get workspace
-------------

To get a single workspace information, you can use this command: ::

    zdm workspace get uid

where :samp:`uid` is the workspace uid.

    
.. _zdm-cmd-workspace-create:

Workspace creation
------------------

To create a new workspace on the ZDM use the command: ::

    zdm workspace create name

where :samp:`name` is the name that you want to give to your new workspace

You can also insert a description of your workspace adding the option :option:`--description desc`

    
.. _zdm-cmd-workspace-tag:

List tags
---------

When a device publish data to the ZDM it label them with a string called tag. With the following command you can see all the tags
that devices associated to your workspace used as data label. ::

    zdm workspace tags uid

where :samp:`uid` is the uid of the workspace

    
.. _zdm-cmd-workspace-data:

Get data
--------

To get all the data of a workspace associated to a tag use the command: ::

    zdm workspace data uid tag

where :samp:`uid` is the uid of the workspace.

    
.. _zdm-cmd-workspace-firmware:

List firmwares
--------------

To have a list of the firmwares you uploaded to the ZDM associated to a workspace use the command: ::

    zdm workspace tags uid

where :samp:`uid` is the uid of the workspace.

    

    
