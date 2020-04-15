.. module:: zerynthzdmclient

.. _zdm-client-main:

*****************************
Zerynth Device Manager Client
*****************************

Zerynth Device Manager can be used for orchestrating both MCU (micro-controller) and CPU (micro-processor) based devices.
If you want to connect a MCU device like a RapsberryPI, a SBC (Single Board Computer) a PC and any Python application general,
the ZDM Client Python Library is what you need.

.. _lib.zerynth.zdmclient:


ZDM Client Python
=================

The Zerynth ZDM Client is a Python implementation of a client of the ZDM.
It can be used to emulate a Zerynth device and connect it to the ZDM.

    
The ZDMClient class
-------------------

.. class:: ZDMClient(device_id, jobs=None, endpoint=ENDPOINT, verbose=False)

    Creates a ZDM client instance with device id :samp:`device_id`. All other parameters are optional and have default values.

    * :samp:`device_id` is the id of the device.
    * :samp:`jobs` is the dictionary that defines the device's available jobs (default None).
    * :samp:`endpoint` is the url of the ZDM broker (default rmq.zdm.zerynth.com).
    * :samp:`verbose` boolean flag for verbose output (default False).

    
.. method:: id(pw)

        Return the device id.
        
.. method:: connect()

        Connect your device to the ZDM. You must set device's password first. It also enable your device to receive incoming messages.
        
.. method:: set_password(pw)

    Set the device password to :samp:`pw`. You can generate a password using the ZDM, creating a key for your device
    
.. method:: publish_data(tag, payload)

    Publish a message to the ZDM.

    * :samp:`tag`, is a label for the device's data into your workspace. More than one device can publish message to the same tag
    * :samp:`payload` is the message payload, represented by a dictionary
