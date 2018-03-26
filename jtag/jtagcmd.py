from base import *
from .jtag import Probe
import click
import threading
import time
import requests
import sys

# Load here because other modules can call this module functions without accessing probe group comands
_interfaces = fs.get_yaml(fs.path(fs.dirname(__file__),"probes.yaml"),failsafe=True)

@cli.group(help="Manage probes.")
def probe():
    pass

@probe.command("list",help="List available probes")
def probe_list():
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
    e,_,_ = proc.runcmd(dev.jtag_tool or "openocd","-f",jtag_interface,"-f",jtag_target,outfn=log)
    


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

    if env.human:
        info("chip id:",chipid)
        info(" vm uid:",vmuid)
    else:
        log_json({"chipid":chipid,"vmuid":vmuid})



def interface_to_script(interface):
    return _interfaces.get(interface,{}).get("script")



############### GDBGUI

@cli.group("debugger",help="Debugging sessions")
def debugger():
    pass


@debugger.command()
@click.argument("target")
def start(target):
    dev = tools.get_target(target)
    if not dev:
        fatal("Can't find device!")
    gdbgui = tools["gdbgui"]
    gdb = tools[dev.cc]["gdb"]
    log(gdb)
    gdb="/home/giacomo/Downloads/gcc-arm-none-eabi-7-2017-q4-major/bin/arm-none-eabi-gdb"
    sys.path = ["/home/giacomo/.zerynth2_test/sys/gdbgui"]+sys.path
    from gdbgui.backend import main
    sys.argv = ["",gdbgui,"-g",gdb]
    main()
    # e,out,_ = proc.runcmd("python",gdbgui,"-g",gdb,"--hide_gdbgui_upgrades","-n",outfn=info,shell=True)
    # if e:
    #     fatal("GDB exited with:",out)
    # else:
    #     info("Debug session closed")
     


@debugger.command()
def stop():
    try: 
        #retrieve main page
        rr = requests.get("http://127.0.0.1:5000/")
    except:
        warning("Can't connect to gdbgui!")
        return
    #search for csrf_token
    matcher = re.compile(".*\"csrf_token\":\s*\"([0-9a-z]+)\".*")
    lines = rr.text.split("\n")
    for line in lines:
        mm = matcher.match(line)
        if mm:
            csrf_token = mm.group(1)
            break
    else:
        fatal("Somethin wrong while retrieving gdbgui info")

    #save cookie
    jar = rr.cookies
    #request shutdown with GET: this saves the csrf token in the session: https://github.com/cs01/gdbgui/blob/master/gdbgui/backend.py#L489
    rr = requests.get("http://127.0.0.1:5000/shutdown",params={"csrf_token":csrf_token},cookies=jar)
    #now POST a shutdown
    rr = requests.post("http://127.0.0.1:5000/_shutdown",params={"csrf_token":csrf_token},headers={"x-csrftoken":csrf_token},cookies=jar)
    info("Done")

