from base import *
from .jtag import Probe
import click
import threading
import time


# Load here because other modules can call this module functions without accessing probe group comands
_interfaces = fs.get_yaml(fs.path(fs.dirname(__file__),"probes.yaml"),failsafe=True)

@cli.group(help="Manage probes.")
def probe():
    pass

@probe.command(help="List available probes")
def list():
    if env.human:
        table = []
        for intf,iinfo in _interfaces.items():
            table.append([intf,iinfo.get("name","---"),iinfo.get("script","---")])
        log_table(table,headers=["probe","name","script"])
    else:
        log_json(_interfaces)


@probe.command(help="Start probe")
@click.argument("target")
@click.argument("probe")
def start(target,probe):
    start_probe(target,probe)


def start_temporary_probe(target,probe):
    info("Starting temporary probe...")
    thread = threading.Thread(target=start_probe, args = (target,probe))
    thread.start()
    pb = Probe()
    for attempt in range(5):
        try:
            info("Checking probe health...")
            pb.connect(0.5)
            pb.send("exit")
            info("Ok")
            return thread
        except Exception as e:
            time.sleep(1)
            continue
    else:
        warning("Temporary probe may be dead...")
        
    return thread

def stop_temporary_probe(tp):
    probe = Probe()
    probe.connect()
    probe.send("shutdown")
    info("Waiting temporary probe...")
    tp.join()
    info("Stopped temporary probe...")



def start_probe(target,probe):
    dev = tools.get_target(target)
    if not dev:
        fatal("Can't find target",target)
    jtagdir = tools.get_tool_dir("openocd")
    if not jtagdir:
        fatal("Can't find OpenOCD!")
    interface_script = interface_to_script(probe)
    if not interface_to_script:
        fatal("Can't find interface!")
    target_script = dev.jtag_target
    if not target_script:
        fatal("Target does not support jtag!")
    
    jtag_interface = fs.path(jtagdir,"scripts","interface",interface_script)
    jtag_target = fs.path(jtagdir,"scripts","target",target_script)
    info("Starting OpenOCD...")
    debug(jtag_interface,jtag_target)
    e,_,_ = proc.runcmd("openocd","-f",jtag_interface,"-f",jtag_target,outfn=log)
    


@probe.command(help="Query a running probe")
@click.argument("commands",nargs=-1)
def send(commands):
    if not commands:
        return
    probe = Probe()
    probe.connect()
    for command in commands:
        probe.send(command)
        for line in probe.read_lines():
            if line!=command:
                #do not print echo
                log(line)
    probe.disconnect()

@probe.command(help="Inspect a device by probe")
@click.argument("target")
@click.argument("probe")
def inspect(target,probe):
    dev = tools.get_target(target)
    if not dev:
        fatal("Can't find target",target)
    if not dev.get_chipid:
        fatal("Target does not support probes!")
    
    # start temporary probe
    tp = start_temporary_probe(target,probe) 
    try:
        chipid = dev.get_chipid()
        vmuid = dev.get_vmuid()
    except Exception as e:
        fatal("Error",e)
    finally:
        # stop temporary probe
        stop_temporary_probe(tp)
    if not chipid:
        fatal("Can' retrieve chip id!")
    if not vmuid:
        fatal("Can' retrieve vm uid!")

    info("chip id:",chipid)
    info(" vm uid:",vmuid)



def interface_to_script(interface):
    return _interfaces.get(interface,{}).get("script")
