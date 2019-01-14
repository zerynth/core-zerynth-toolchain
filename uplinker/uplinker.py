from base import *
from packages import *
from .relocator import Relocator
import click
import time
import re
import struct
import base64
from jtag import *
import virtualmachines
from devices import get_device, get_device_by_target,probing




def handshake(ch):
    # HANDSHAKE 1
    line=""
    ch.write("U") # ask for bytecode uplink
    info("Handshake")
    frlines = 0
    while not line.endswith("OK\n"):
        line=ch.readline()
        if (not line) or frlines>5:
            #timeout without an answer
            fatal("Timeout without answer")
        frlines+=1
    #line=ch.readline()

    # read symbols
    symbols = []
    nsymbols=3#int(line.strip("\n"),16)
    info("    symbols:",nsymbols)
    # for sj in range(0,nsymbols-3):
    #     line=ch.readline()
    #     debug(line)
    #     if not line:
    #         fatal("Bad symbol exchange")
    #     symbols.append(int(line.strip("\n"),16))

        #self.log("    vmsym  @"+line.strip("\n"))

    line=ch.readline()
    debug(line)
    _memstart = int(line.strip("\n"),16)
    info("    membase  @"+line.strip("\n"))

    line=ch.readline()
    debug(line)
    _romstart = int(line.strip("\n"),16)
    info("    romstart @"+line.strip("\n"))

    line=ch.readline()
    debug(line)
    _flashspace = int(line.strip("\n"),16)
    info("    flash    @"+line.strip("\n"))

    return symbols,_memstart,_romstart,_flashspace

@cli.command(help="Uplink bytecode to a device. \n\n Arguments: \n\n ALIAS: device alias. \n\n BYTECODE: path to a bytecode file.")
@click.argument("alias")
@click.argument("bytecode",type=click.Path())
@click.option("--loop",default=5,type=click.IntRange(1,20),help="number of retries during device discovery.")
def uplink(alias,bytecode,loop):
    """
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



    """
    dev = get_device(alias,loop)
    _uplink_dev(dev,bytecode,loop)

@cli.command(help="Uplink bytecode to a configured device")
@click.argument("target")
@click.argument("bytecode",type=click.Path())
@click.option("--loop",default=5,type=click.IntRange(1,20),help="number of retries during device discovery.")
@click.option("--spec","__specs",default="",multiple=True)
def uplink_raw(target,bytecode,loop,__specs):
    """
.. _ztc-cmd-uplink-raw:

Uplink (raw)
============

It is possible to perform an uplink against a configured device by specifying th relevant device parameters as in the :ref:`register raw <ztc-cmd-device-register-raw>` command, by specifying the :samp:`port` parameter.

The command: ::

    ztc uplink_raw target bytecode --spec port:the_port

performs an uplink on the device of type :samp:`target` using the bytecode file at :samp:`bytecode` using the serial prot :samp:`port`.

    """
    options = {}
    for spec in __specs:
        pc = spec.find(":")
        if pc<0:
            fatal("invalid spec format. Give key:value")
        options[spec[:pc]]=spec[pc+1:]
    dev = get_device_by_target(target,options)
    _uplink_dev(dev,bytecode,loop)

@cli.command(help="Uplink bytecode to a device using a probe.")
@click.argument("target")
@click.argument("probe")
@click.argument("linked_bytecode",type=click.Path())
@click.option("--address",default="")
def uplink_by_probe(target,probe,linked_bytecode,address):
    """
.. _ztc-cmd-uplink-by-probe:

Uplink by probe
===============

It is possible to perform an uplink against a configured device by using a probe. Contrary to other uplink commands that require a bytecode file argument, the :samp:`uplink_by_probe` command requires a linked bytecode file argument (obtained with the :ref:`link <ztc-cmd-link>` command).

The command: ::

    ztc uplink_by_probe target probe linked_bytecode

perform an uplink on the device type :samp:`target` using probe :samp:`probe` to transfer the :samp:`linked_bytecode` file to the running VM.
It is possible to change the address where the bytecode will be flashed by specifying the :option:`--address` option followed by the hexadecimal representation of the address (useful for OTA VMs scenarios)

    """
    dev = get_device_by_target(target,{},skip_reset=True)
    if not dev.jtag_capable:
        fatal("Target does not support probes!")
    tp = start_temporary_probe(target,probe)
    res,out = dev.burn_with_probe(fs.readfile(linked_bytecode,"b"),offset=address or dev.bytecode_offset)
    stop_temporary_probe(tp)
    if res:
        info("Uplink done")
    else:
        fatal("Uplink failed:",out)

def _uplink_dev(dev,bytecode,loop):
    try:
        bf = fs.get_json(bytecode)
    except:
        fatal("Can't open file",bytecode)

    vm_chunk = dev.get("vm_chunk",4096)
    vm_mini_chunk = dev.get("vm_mini_chunk",4096)
    vm_fragmented_upload = dev.get("vm_fragmented_upload",None)

    if not dev.port:
        fatal("Device has no serial port! Check that drivers are installed correctly...")
    # open channel to dev TODO: sockets
    conn = ConnectionInfo()
    conn.set_serial(dev.port,**dev.connection)
    ch = Channel(conn)
    try:
        ch.open(timeout=2)
    except:
        fatal("Can't open serial:",dev.port)

    try:
        version,vmuid,chuid,target = probing(ch,dev.target, True if not dev.fixed_timeouts else False)
    except Exception as e:
        if dev.uplink_reset:
            fatal("Something wrong during the probing phase: too late reset or serial port already open?")
        else:
            fatal("Something wrong during the probing phase:",e)

    vms = tools.get_vm(vmuid,version,chuid,target)
    if not vms:
        ch.close()
        warning("No such vm for",dev.target,"with id",vmuid," ==> searching online...")
        virtualmachines.download_vm(vmuid)
        info("VM downloaded, retry uplinking!")
        return

    vm = fs.get_json(vms)

    symbols,_memstart,_romstart,_flashspace = handshake(ch)

    relocator = Relocator(bf,vm,dev)
    thebin = relocator.relocate(symbols,_memstart,_romstart)
    totsize = len(thebin)

    #self.log("Sending %i bytes..."%totsize)
    if totsize>_flashspace:
        #logger.info("Not enough space on board! Needed %i bytes, available %i bytes",totsize,_flashspace)
        #self.log("Not enough space on board! Needed "+str(totsize)+" bytes, available "+str(_flashspace)+" bytes")
        #raise UplinkException("Not enough space on board!")
        fatal("Not enough space on device")
    else:
        info("Erasing flash")
        #logger.info("Erasing flash...")
        #self.log("Erasing flash...")

    # send total size
    bsz = struct.pack("<I",totsize)
    ch.write(bsz)
    #for b in bsz:
    #    ch.write(bytes([b]))

    starttime = time.perf_counter()
    while time.perf_counter()-starttime<10:
        line=ch.readline()
        debug(line)
        if line=="OK\n":
            #logger.info("OK")
            break
        #else:
            #logger.info("%s",line)
    else:
        fatal("Can't send bytecode")

    #logger.info("Sending Bytecode: %i bytes (available %i)",totsize,_flashspace)
    #self.log("Sending Bytecode: "+str(totsize)+" bytes (available "+str(_flashspace)+")")
    info("Sending Bytecode:",totsize,"bytes ( available",_flashspace,")")

    wrt = 0
    ll = len(thebin)
    nblock = 0
    nattempt = 0
    jattempt = 0
    #ser.settimeout(2)
    while ll>0 and nattempt<3:
        tosend = min(ll,vm_chunk)
        buf = thebin[wrt:wrt+tosend]
        adler = adler32(buf)
        debug("sending block %i of %i bytes with crc: %x"%(nblock,tosend,adler))
        for x in range(0,len(buf),vm_mini_chunk):
            ch.write(buf[x:x+vm_mini_chunk])
        ch.write(struct.pack("<I",adler))
        #ser.flush()
        jattempt=0
        while jattempt<200: #avoid debug messages (starting with .)
            line=ch.readline()
            debug("read line: %s attempt %s"%(line,str(jattempt)))
            jattempt+=1
            if line and not line.startswith("."):
                break
        if line=="OK\n":
            #logger.info("OK")
            nblock+=1
            wrt+=len(buf)
            ll-=tosend
            nattempt=0
            continue
        elif line=="RB\n":
            #logger.info("ERR! resending")
            nattempt+=1
            continue
        else:
            #logger.error("Failed")
            fatal("Failed while sending bytecode",line)
    if nattempt!=0:
        ch.close()
        fatal("Too many attempts")
    else:
        ch.close()
        info("Uplink done")



@cli.command(help="Generate bytecode runnable on a specific VM. \n\n Arguments: \n\n VMUID: VM identifier. \n\n BYTECODE: path to a bytecode file.")
@click.argument("vmuid")
@click.argument("bytecode",type=click.Path())
@click.option("--include_vm",default=False, flag_value=True,help="Generate a binary with VM included (not compatible with OTA!)")
@click.option("--otavm",default=False, flag_value=True,help="Include OTA VM together with bytecode")
@click.option("--vm","vm_ota",default=0, type=int,help="Select OTA VM index")
@click.option("--bc","bc_ota",default=0, type=int,help="Select OTA VM Bytecode index")
@click.option("--file",default="", type=str,help="Save binary to specified file")
@click.option("--vmfile",default="", type=str,help="Save binary to specified file")
@click.option("--bin",default=False,flag_value=True,help="Save in binary format")
@click.option("--debug_bytecode",default=False,flag_value=True,help="Save debug info in bytecode")
def link(vmuid,bytecode,include_vm,vm_ota,bc_ota,file,otavm,bin,debug_bytecode,vmfile):
    """
.. _ztc-cmd-link:

Link
====

The command: ::

    ztc link vmuid bytecode

generates a file containing the bytecode :samp:`bytecode` modified in such a way that it can be executed on the VM :samp:`vmuid` without the need for an uplink.

This command is mainly used to generate executable bytecode for FOTA updates. Alternatively it can be used to generate a binary firmware to be manually flashed on a device, skipping both device recognition and uplinking.

It takes the following options:

* :option:`--vm n`, for FOTA enabled VMs, generate a bytecode that can be executed by a VM running on slot :samp:`n`. Default :samp:`n` is zero.
* :option:`--bc n`, for FOTA enabled VMs, generate a bytecode that can be executed by on bytecode slot :samp:`n`. Default :samp:`n` is zero.
* :option:`--include_vm`, generate a single binary containing both the VM and the bytecode, ready to be flashed on the device. Not compatible with FOTA VMs!
* :option:`--otavm`, generate both bytecode and VM ready for a FOTA update
* :option:`--file file`, save the output to file :samp:`file`

FOTA updates
------------

Generating firmware for FOTA updates can be tricky. The following information is needed:

    * The VM unique identifier, :samp:`vmuid`
    * The unique identifier of a new FOTA enabled VM, :samp:`vmuid_new`
    * The current slot the VM is running on, :samp:`vmslot`. Can be retrieved with :ref:`fota library <stdlib.fota>`
    * The current slot the bytecode is running on, :samp:`bcslot`, Can be retrieved with :ref:`fota library <stdlib.fota>`

For example, assuming a project has been compiled to the bytecode file :samp:`project.vbo` and :samp:`vmslot=0` and :samp:`bcslot=0`, the following commands can be given: ::


    # generate bytecode capable of running on slot 1 with VM in slot 0
    # the resulting file can be used for a FOTA update of the bytecode
    ztc link vmuid project.vbo --bc 1 --file project.vbe

    # generate bytecode capable of running on slot 1 with VM in slot 1
    # the resulting file CAN'T be used for a FOTA update because the running VM is in slot 0
    # and project.vbe does not contain the new VM
    ztc link vmuid_new project.vbo --bc 1 --vm 1 --file project.vbe

    # generate bytecode capable of running on slot 1 with VM in slot 1
    # the resulting file can be used for a FOTA update of the bytecode and VM
    # because project.vbe contains the new VM
    ztc link vmuid_new project.vbo --bc 1 --vm 1 --otavm --file project.vbe


.. note:: It is not possible to generate a FOTA update of the VM only!

.. note:: To generate a Zerynth ADM compatible FOTA bytecode update, add option :option:`-J` before the link command. The resulting file will be JSON and not binary.


    """
    vms = tools.get_vm_by_uid(vmuid)
    if not vms:
        warning("No such vm with uid",vmuid," ==> searching online...")
        virtualmachines.download_vm(vmuid)
        vms = tools.get_vm_by_uid(vmuid)
        if not vms:
            fatal("Unexpected error searching for vm",vmuid)

    vm = fs.get_json(vms)

    try:
        bf = fs.get_json(bytecode)
    except:
        fatal("Can't open file",bytecode)

    if vm_ota:
        if "ota" not in vm:
            fatal("This VM does not support OTA!")
        else:
            vm = vm["ota"]
    symbols = vm["map"]["sym"]
    _memstart = int(vm["map"]["memstart"],16)+vm["map"]["memdelta"]
    _romstart = int(vm["map"]["bc"][bc_ota],16)+int(vm["map"]["bcdelta"],16)

    debug("MEMSTART: ",hex(_memstart))
    debug("ROMSTART: ",hex(_romstart))
    relocator = Relocator(bf,vm,Var(
        {
            "relocator":vm["relocator"],
            "cc":vm["cc"],
            "gccopts":vm["gccopts"],
            "rodata_in_ram":vm.get("rodata_in_ram",False)
        },recursive=False))
    addresses = []#[int(symbols[x],16) for x in relocator.vmsym]
    dbginfo = []
    thebin = relocator.relocate(addresses,_memstart,_romstart,dbginfo)
    bcbin = thebin

    if debug_bytecode:
        if dbginfo:
            dbgbin = fs.readfile(dbginfo[0],"b")
            bf["dbg"]={}
            bf["dbg"]["address"] = hex(dbginfo[1])
            bf["dbg"]["info"] = base64.b64encode(dbgbin).decode("utf-8")
            fs.set_json(bf,bytecode)

    if include_vm:
        if vm_ota or bc_ota:
            fatal("Can't include OTA VM together with bytecode")
        if isinstance(vm["bin"],list):
            fatal("Fragmented VM not supported!")
        vmbin = bytearray(base64.standard_b64decode(vm["bin"]))
        _vmstart = int(vm["map"]["vm"][vm_ota],16)
        vmsize = len(vmbin)
        gapzone = _romstart-_vmstart-vmsize
        vmbin.extend(b'\xff'*gapzone)
        vmbin.extend(thebin)
        thebin = vmbin


    if not env.human:
        res = {
            "bcbin":base64.b64encode(bcbin).decode("utf-8"),
            "vmbin":"" if not otavm else ota_prepare_vm(vm),
            "bc_idx": bc_ota,
            "bc":vm["map"]["bc"][bc_ota],
            "vm_idx": vm_ota,
            "vm": vm["map"]["vm"][vm_ota],
            "has_vm": include_vm,
            "vmuid":vmuid
        }
        if file:
            if bin:
                fs.write_file(thebin,file)
            else:
                fs.set_json(res,file)
        else:
            log_json(res)

        if vmfile and otavm and bin:
            fs.write_file(base64.b64decode(res["vmbin"]),vmfile)
            info("File",vmfile,"saved")
            fs.write_file(base64.b64decode(res["bcbin"]),file)
            info("File",file,"saved")
    else:
        if file:
            fs.write_file(thebin,file)
            info("File",file,"saved")



def ota_prepare_vm(vm):
    if isinstance(vm["bin"],str):
        # single file vm
        return vm["bin"]
    else:
        bin_indexes = vm["vm_indexes"]
        debug(bin_indexes)
        bin = bytearray()
        for i in bin_indexes:   # add one after the other the various vm segments
            b64c = vm["bin"][i]
            bb =base64.b64decode(bytes(b64c,"utf8")) 
            debug("adding segment",i,len(bb),hex(bb[0]))
            bin.extend(bb)
        return base64.b64encode(bin).decode("utf-8")
        # multi file vm


def adler32(buf):
    a = 1
    b = 0
    for x in buf:
        a = (a+x)%65521
        b = (b+a)%65521
    return (b<<16)|a


