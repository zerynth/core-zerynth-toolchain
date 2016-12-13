"""
.. _ztc-cmd-uplink_

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
from base import *
from .relocator import Relocator
import click
import devices
import time
import re
import struct

def get_device(alias,loop):
    _dsc = devices.Discover()
    uids = []
    adev = _dsc.search_for_device(alias)
    if not adev:
        fatal("Can't find device",alias)
    elif isinstance(adev,list):
        fatal("Ambiguous alias",[x.alias for x in adev])
    uid = adev.uid

    # search for device
    info("Searching for device",uid,"with alias",alias)
    uids, devs = _dsc.wait_for_uid(uid,loop=loop)
    if not uids:
        fatal("No such device",uid)
    elif len(uids)>1:
        fatal("Ambiguous uid",uids)
    uid = uids[0]
    for k,d in devs.items():
        if d.uid == uid:
            dev = d
            hh = k
            break
    else:
        fatal("Error!",uid)
    # got dev object!
    if dev.uplink_reset:
        info("Please reset the device!")
        sleep(dev.reset_time/1000)
        info("Searching for device",uid,"again")
        # wait for dev to come back, port/address may change -_-
        uids,devs = _dsc.wait_for_uid(uid)
        if len(uids)!=1:
            fatal("Can't find device",uid)
    dev = devs[hh]
    return dev

def probing(ch,devtarget):
    # PROBING
    starttime = time.perf_counter()
    probesent = False
    hcatcher = re.compile("^(r[0-9]+\.[0-9]+\.[0-9]+) ([0-9A-Za-z_\-]+) ([^ ]+) ([0-9a-fA-F]+) ZERYNTH")
    while time.perf_counter()-starttime<5:
        line=ch.readline()
        if not line and not probesent:
            probesent=True
            ch.write("V")
            info("Probe sent")
        line = line.replace("\n","").strip()
        if line:
            info("Got header:",line)
        if line.endswith("ZERYNTH"):
            mth = hcatcher.match(line)
            if mth:
                version = mth.group(1)
                vmuid = mth.group(2)
                chuid = mth.group(4)
                target = mth.group(3)
                break
    else:
        fatal("No answer to probe")

    if target!=devtarget:
        fatal("Wrong VM: uplinking for",devtarget,"and found",target,"instead")
    else:
        info("Found VM",vmuid,"for",target)

    return version,vmuid,chuid,target



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
    line=ch.readline()

    # read symbols
    symbols = []
    nsymbols=int(line.strip("\n"),16)
    info("    symbols:",nsymbols)
    for sj in range(0,nsymbols-3):
        line=ch.readline()
        if not line:
            fatal("Bad symbol exchange")
        symbols.append(int(line.strip("\n"),16))

        #self.log("    vmsym  @"+line.strip("\n"))
        
    line=ch.readline()
    _memstart = int(line.strip("\n"),16)
    info("    membase  @"+line.strip("\n"))
    
    line=ch.readline()
    _romstart = int(line.strip("\n"),16)
    info("    romstart @"+line.strip("\n"))

    line=ch.readline()
    _flashspace = int(line.strip("\n"),16)
    info("    flash    @"+line.strip("\n"))

    return symbols,_memstart,_romstart,_flashspace

@cli.command(help="Uplink bytecode to a device. \n\n Arguments: \n\n ALIAS: device alias. \n\n BYTECODE: path to a bytecode file.")
@click.argument("alias")
@click.argument("bytecode",type=click.Path())
@click.option("--loop",default=5,type=click.IntRange(1,20),help="number of retries during device discovery.")
def uplink(alias,bytecode,loop):
    try:
        bf = fs.get_json(bytecode)
    except:
        fatal("Can't open file",bytecode)

    dev = get_device(alias,loop)
    vm_chunk = dev.get("vm_chunk",4096)
    vm_fragmented_upload = dev.get("vm_fragmented_upload",None)

    # open channel to dev TODO: sockets
    conn = ConnectionInfo()
    conn.set_serial(dev.port,**dev.connection)
    ch = Channel(conn)
    try:
        ch.open(timeout=2)
    except:
        fatal("Can't open serial:",dev.port)

    try:
        version,vmuid,chuid,target = probing(ch,dev.target)
    except:
        if dev.uplink_reset:
            fatal("Something wrong during the probing phase: too late reset?")
        else:
            fatal("Something wrong during the probing phase:",e)

    vms = tools.get_vm(vmuid,version,chuid,target)
    if not vms:
        ch.close()
        fatal("No such vm for",dev.target,"with id",vmuid)
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
        #info("sending block %i of %i bytes with crc: %x",nblock,tosend,adler)
        ch.write(buf)
        ch.write(struct.pack("<I",adler))
        #ser.flush()
        jattempt=0
        while jattempt<200: #avoid debug messages (starting with .)
            line=ch.readline()
            #logger.info("read line: %s attempt %s",line,str(jattempt))
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
            raise UplinkException("Failed while sending bytecode")
    if nattempt!=0:
        ch.close()
        fatal("Too many attempts")
    else:
        ch.close()
        info("Uplink done")

def adler32(buf):
    a = 1
    b = 0
    for x in buf:
        a = (a+x)%65521
        b = (b+a)%65521
    return (b<<16)|a
