.. _ztc-cmd-uplink:

Uplink
======

Once a Zerynth program is compiled to bytecode it can be executed by transferring such bytecode to a running virtual machine on a device. 
This operation is called "uplinking" in the ZTC terminology.

Indeed Zerynth virtual machines act as a bootloader waiting a small amount of time after device reset to check if new bytecode is incoming.
If not, they go on executing a previously loaded bytecode or just wait forever.

The command: ::

    ztc uplink alias bytecode

will start the uplinking process for the device with alias :samp:`alias` using the compiled :samp:`.vbo` file given in the :samp:`bytecode` argument. As usual :samp:`alias` ca be partially specified.

The uplinking process may require user interaction for manual resetting the device whan appropriate. The process consists of:

* a discovery phase: the device with the given alias is searched and its attributes are checked
* a probing phase: depending on the device target a manual reset can be asked to the user. It is needed to reset the virtual machine and put it in a receptive state. In this phase a "probe" is sent to the virtual machine, asking for runtime details
* a handshake phase: once runtime details are known, additional info are exchanged between the linker and the virtual machine to ensure correct bytecode transfer
* a relocation phase: the bytecode is not usually executable as is and some symbols must be resolved against runtime details
* a flashing phase: the relocated bytecode is sent to the virtual machine

Each of the previous phases may fail in different ways and the cause can be determined by inspecting error messages.

The :command:`uplink` may the additional :option:`--loop times` option that specifies the number of retries during the discovery phase (each retry lasts one second). 
