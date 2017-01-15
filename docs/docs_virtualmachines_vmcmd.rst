.. _ztc-cmd-vm:

****************
Virtual Machines 
****************

Virtual machines are the core of Zerynth. From the point of view of the ZTC, a virtual machine is a binary blob to be flashed on a device
in order to enable Zerynth code execution. Virtual machines are tied to the unique identifier of the device microcontroller, therefore for each microcontroller a specific virtual machine must be created.

Virtual machines can be managed with the following commands:

* :ref:`create <ztc-cmd-vm-create>`
* :ref:`list <ztc-cmd-vm-list>`
* :ref:`available <ztc-cmd-vm-available>`

    
.. _ztc-cmd-vm-create:

Create a Virtual Machine
------------------------

Virtual machine can be created with custom features for a specific device. Creation consists in requesting a virtual machine unique identifier (:samp:`vmuid`) to the Zerynth backend for a registered device.

The command: ::

    ztc vm create alias version rtos

executes a REST call to the Zerynth backend asking for the creation of a virtual machine for the registered device with alias :samp:`alias`. The created virtual machine will run on the RTOS specified by :samp:`rtos` using the virtual machine release version :samp:`version`.

It is also possible to specify the additional option :option:`--feat feature` to customize the virtual machine with :samp:`feature`. Some features are available for pro accounts only. Multiple features can be specified repeating the option.

If virtual machine creation ends succesfully, the virtual machine binary is also downloaded and added to the local virtual machine storage. The :samp:`vmuid` is printed as a result.

    
.. _ztc-cmd-vm-list:

List Virtual Machines
---------------------

The list of created virtual machines can be retrieved with the command: ::

    ztc vm list

The retrieved list contains at most 50 virtual machines.

Additional options can be provided to filter the returned virtual machine set:

* :option:`--from n`, skip the first :samp:`n` virtual machines
* :option:`--core_dep version`, returns only the virtual machines compatible with Zerynth version :samp:`version`.

    
.. _ztc-cmd-vm-available:

Virtual Machine parameters
--------------------------

For each device target a different set of virtual machines can be created that takes into consideration the features of the hardware. Not every device can run every virtual machine. The list of available virtual machines for a specific target can be retrieved by: ::

    ztc vm available target

For the device target, a list of possible virtual machine configurations is returned with the following attributes:

* virtual machine version 
* RTOS
* additional features
* free/pro only

    
