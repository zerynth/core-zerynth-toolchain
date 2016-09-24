from base import *
import click
import devices


@cli.command()
@click.argument("uid",)
@click.argument("bytecode")
@click.option("--loop",default=5,type=click.IntRange(1,20))
def uplink(uid,bytecode,loop):
    _dsc = devices.Discover()
    uids = []
    # search for device #TODO: search for alias
    info("Searching for device",uid)
    uids, devs = _dsc.wait_for_uid(uid)
    if not uids:
        fatal("No such device",uid)
    elif len(uids)>1:
        fatal("Ambiguous uid",uids)
    uid = uids[0]
    dev = devs[uid]
    # got dev object!
    if dev.uplink_reset:
        info["Please reset the device!"]
        sleep(dev.reset_time)
    # wait for dev to come back, port/address may change -_-
    uids,devs = _dsc.wait_for_uid(uid)
    if len(uids)!=1:
        fatal("Can't find device",uid)
    uid = uids[0]
    dev = devs[uid]

    # open channel to dev
    conn = ConnectionInfo()
    conn.set_serial(dev.port,*dev.connection)
    ch = Channel(conn)








class Uplinker():
    pass