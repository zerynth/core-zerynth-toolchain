from base import *
from devices import get_device_by_target
import click
import base64

@cli.group(help="Manage mass programming.")
def massprog():
    pass

@massprog.command("start",help="Start mass programming")
@click.argument("mppath")
def mp_start(mppath):
    """
    """
    mapfile = fs.path(mppath,"zmap.yml")
    map = fs.get_yaml(mapfile)
    config = map["config"]
    target = config["target"]
    register = config["register"]
    project = config["project"]
    shareable = config.get("sharable",False)
    vmuid = config["vm"]
    dev_options = config.get("dev",{})
    options = config.get("options",{})
    provisioning = map.get("provisioning",{})
    layout = {"bin":[],"loc":[],"dsc":[]}



    # check for binary fw
    info("===== Firmware")
    fwbin = fs.path(mppath,"fw.bin")
    if not fs.exists(fwbin):
        warning("No binary bytecode present, checking vbo for",project)
        bytecode = fs.path(mppath,"fw.vbo")
        if not fs.exists(bytecode):
            warning("No bytecode present either, compiling project at",project)
            res, out, _ = proc.run_ztc("compile",project,target,"-o",fs.path(mppath,"fw.vbo"),outfn=log)
            if res:
                fatal("Can't compile project at",project)
        res, out, _ = proc.run_ztc("link",vmuid,bytecode,"--bin","--file",fs.path(mppath,"fw.bin"),outfn=log)
        if res:
            fatal("Can't link project at",project)
    info("     using",fwbin)

    info("===== VM")
    dev = get_device_by_target(target,dev_options,skip_reset=True)
    # get vm bin
    vmfile = tools.get_vm_by_uid(vmuid)
    vm = fs.get_json(vmfile)
    vmpath = fs.path(mppath,vmuid)
    if not fs.exists(vmpath):
        fs.makedirs(vmpath)
        if isinstance(vm["bin"],str):
            vmbin  = bytearray(base64.standard_b64decode(vm["bin"]))
            vmbinfile = fs.path(vmpath,"vm.bin")
            fs.write_file(vmbin,vmbinfile)
            vmloc = vm["loc"]
            layout["bin"].append(vmbinfile)
            layout["loc"].extend(vmloc)
            layout["dsc"].append("VM")
        else:
            vmbin=[base64.standard_b64decode(x) for x in vm["bin"]]
            for i,vv in enumerate(vmbin):
                vmbinfile = fs.path(vmpath,"vm"+str(i)+".bin")
                fs.write_file(vv,vmbinfile)
                layout["bin"].append(vmbinfile)
                layout["dsc"].append("VM fragment "+str(i))
            vmloc = vm["loc"]
            layout["loc"].extend(vmloc)
    info("     using",vmpath)

    layout["bin"].append(fwbin)
    layout["loc"].extend(vm["bcloc"])
    layout["dsc"].append("Firmware")


    info("===== Registration")
    chipid = dev.custom_get_chipid(outfn=info)
    if not chipid:
        fatal("Can't find chipid!")

    info("===== Licensing")
    # get vm binary
    # call single endpoint for reg+vm
    # patch vm

    if provisioning:
        info("===== Provisioning")
        # start provisioning

    info("===== Layout")
    table = []
    for i in range(len(layout["bin"])):
        table.append([layout["dsc"][i],layout["loc"][i],layout["bin"][i]])
    log_table(table,headers=["Segment","Address","File"])

    info("===== Burn Layout")
    # burn layout
    dev.burn_layout(layout,options,outfn=info)



