.. _ztc-cmd-provisioning:

************
Provisioning
************

The Zerynth Toolchain allows to easily provision cryto elements by means of the ``provisioning`` commands group.


    
.. _ztc-cmd-provisioning-uplink_config_firmware:

Uplink Configurator Firmware to the device
------------------------------------------

The command: ::

    ztc provisioning uplink-config-firmware device_alias

Performs a preliminary step for subsequent provisioning commands.
A Configurator firmware is compiled and flashed onto the device, with alias :samp:`alias`, the crypto element to provision is plugged to.
The Configurator makes the device ready to accept serial commands which will be translated into provisioning actions.

The implementation of the Configurator is dependent on target cryptoelement, but not on the device used to provision it.

Available command options are:

* :option:`--cryptofamily family`, to specify the family of the crypto element to provision (at the moment ``ateccx08a`` is the only supported  option). Default :samp:`family` is ``ateccx08a``;
* :option:`--cryptodevice device`, to specify the device, from those available in chosen family, to provision. For ``ateccx08a`` family, devices ``atecc508a`` and ``atecc608a`` are supported and can be chosen with a :samp:`device` value of ``5`` or ``6`` respectively. Default :samp:`device` value depends on chosen family: ``5`` for ``ateccx08a`` family;
* :option:`--i2caddr address`, to specify the i2c address of the crypto element. Needed only if the crypto element uses an i2c interface. Default :samp:`address` value depends on chosen family: ``0x60`` for ``ateccx08a`` family;
* :option:`--i2cdrv drv`, to specify the device i2c driver the crypto element is plugged to. Needed only if the crypto element uses an i2c interface. :samp:`drv` can be ``I2C0``, ``I2C1``, ... . Default :samp:`drv` value is ``I2C0``.

    
.. warning:: It is mandatory for the following commands to correctly execute to flash the Configurator firmware first.

.. _ztc-cmd-provisioning-read_config:

Read Crypto Element Configuration
---------------------------------

The command: ::

    ztc provisioning read-config device_alias

Reads and outputs the configuration of the crypto element plugged to device with alias :samp:`alias`.

    
.. _ztc-cmd-provisioning-get_public:

Retrieve Public Key
-------------------

The command: ::

    ztc provisioning get-public device_alias private_slot

Retrieves the public key derived from private key stored in :samp:`private_slot` key slot of the crypto element plugged to the device with alias :samp:`device_alias`.

Available command options are:

* :option:`--format pubkey_format`, to specify the output format of the public key: ``pem`` or ``hex``. ``pem`` by default;
* :option:`--output path`, to specify a path to store retrieved public key. If a folder is given, the key is saved to ``public.pubkey_format`` file.

    
.. _ztc-cmd-provisioning-write_config:

Write Crypto Element Configuration
----------------------------------

The command: ::

    ztc provisioning write-config device_alias configuration_file

Writes configuration specified in :samp:`configuration_file` YAML file to the crypto element plugged to device with alias :samp:`device_alias`.

Available command options are:

* :option:`--lock lock_value`, if True locks written configuration;

.. note:: an Example YAML configuration file can be copied to :samp:`configuration_file` path if ``get`` is passed as :samp:`device_alias`.

    
.. _ztc-cmd-provisioning-get_csr:

Get Certificate Signing Request
-------------------------------

The command: ::

    ztc provisioning get-csr device_alias private_slot subject

Retrieves a Certificate Signing Request built on subject :samp:`subject` and signed with private key store in slot :samp:`private_slot` of the crypto element plugged to device with alias :samp:`alias`.

Available command options are:

* :option:`--output path`, to specify a path to store retrieved CSR. If a folder is given, the CSR is saved to ``atecc.csr`` file.
    
.. _ztc-cmd-provisioning-locked:

Locked
------

The command: ::

    ztc provisioning locked device_alias

Outputs the lock state of the crypto elements plugged to device with alias :samp:`alias`.

    
