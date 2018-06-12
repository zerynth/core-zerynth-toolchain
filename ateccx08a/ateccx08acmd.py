# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2018-06-05 17:31:01
# @Last Modified by:   Lorenzo
# @Last Modified time: 2018-06-08 17:52:32

"""
.. _ztc-cmd-ateccx08a:

===================
Microchip ATECCx08a
===================

    """

from base import *
import click

from uplinker import uplinker
from compiler import compilercmd

from . import public_converter
from . import config_parser
from .serialcommander import *
from .utils import *

@cli.group(help="ztc and Microchip ATECCx08a cli integration")
def ateccx08a():
    pass

@ateccx08a.command("uplink-config-firmware", help="uplink configurator firmware")
@click.argument("alias")
@click.option("--i2caddr",default=0x60)
@click.option("--i2cdrv",default=0)
@click.option("--cryptotype",default=5,type=click.Choice([1, 5, 6]))
def __uplink_config_firmware(alias, i2caddr, i2cdrv, cryptotype):
    configurator_firm = fs.path(fs.dirname(__file__), "firmware", "configurator")
    tmpdir = fs.get_tempdir()

    fs.copytree(configurator_firm, tmpdir)

    configurator_conf_path = fs.path(tmpdir, "config.json")
    configurator_conf = fs.get_json(configurator_conf_path)
    configurator_conf["i2caddr"] = i2caddr
    configurator_conf["i2cdrv"]  = i2cdrv
    fs.set_json(configurator_conf, configurator_conf_path)

    loop = 5
    dev = uplinker.get_device(alias,loop,perform_reset=False)
    compilercmd._zcompile(tmpdir, dev.target, False, [], [], False, [], False)

    # reset before uplink
    dev = uplinker.get_device(alias,loop)
    uplinker._uplink_dev(dev,fs.path(tmpdir, "main.vbo"), loop)

    fs.del_tempdir(tmpdir)

def _serial_channel(alias):
    loop = 5
    dev = uplinker.get_device(alias,loop,perform_reset=False)
    if not dev.port:
        fatal("Device has no serial port! Check that drivers are installed correctly...")
    conn = ConnectionInfo()
    conn.set_serial(dev.port,**dev.connection)
    ch = Channel(conn)
    try:
        ch.open(timeout=2)
    except:
        fatal("Can't open serial:",dev.port)
    return ch

@ateccx08a.command("read-config", help="read configuration zone")
@click.argument("alias")
def __read_config(alias):
    cmd_ch = _serial_channel(alias)
    commander = SerialCommander(cmd_ch, info, fatal)
    commander.read_config()

@ateccx08a.command("get-public", help="retrieve public key associated to private in chosen slot")
@click.argument("alias")
@click.argument("private_slot")
@click.option("--format", "pub_format", default="pem", type=click.Choice(["pem","hex"]))
@click.option("--output", "-o", default='', type=click.Path())
def __get_public(alias, private_slot, pub_format, output):
    cmd_ch = _serial_channel(alias)
    commander = SerialCommander(cmd_ch, info, fatal)
    public_key = commander.get_public(int(private_slot))

    if pub_format == "pem":
        formatted_key = public_converter.xytopem(public_key)
        info(" Public key:\n", formatted_key, sep="", end="")
    elif pub_format == "hex":
        formatted_key = public_converter.xytohex(public_key)
        info(" Public key:\n", formatted_key, sep="")

    if output:
        if fs.is_dir(output):
            output=fs.path(output,"public." + pub_format)
        fs.write_file(formatted_key, output)

@ateccx08a.command("gen-private", help="generate private key in chosen slot")
@click.argument("alias")
@click.argument("private_slot")
@click.option("--format", "pub_format", default="pem", type=click.Choice(["pem","hex"]))
def __gen_private(alias, private_slot, pub_format):
    cmd_ch = _serial_channel(alias)
    commander = SerialCommander(cmd_ch, info, fatal)
    public_key = commander.generate_private(int(private_slot))

    if pub_format == "pem":
        formatted_key = public_converter.xytopem(public_key)
        info(" Public key:\n", formatted_key, sep="", end="")
    elif pub_format == "hex":
        formatted_key = public_converter.xytohex(public_key)
        info(" Public key:\n", formatted_key, sep="")

    # if output:
    #     if fs.is_dir(output):
    #         output=fs.path(output,"public." + pub_format)
    #     fs.write_file(formatted_key, output)


def _do_lock(commander, config_crc):
    commander.lock_config_cmd(config_crc)
    commander.lock_data_cmd()

def _do_write_config(commander):
    #00:16  write forbidden
    #16:84  simple write command
    #84:86  update extra command
    #86:88  lock command
    #88:128 simple write command

    current_byte = 0
    while True:
        if current_byte < 16:
            config_parser.config_put_special(commander.getspecial_cmd())
            des_config = config_parser.print_desired_config()
            info(' Desired config (special zone retrieved from device)\n', des_config, end='', sep='')
            config_crc = crc16(config_parser.config_zone_bin)
            # crc is returned LSb first
            info('crc16:', '%02X-%02X' % (config_crc[0], config_crc[1]))
            current_byte += 16
        if current_byte < 84 or (current_byte >= 88 and current_byte < 128):
            commander.write_cmd(current_byte, config_parser.config_zone_bin[current_byte:current_byte+config_parser.word_size])
            current_byte += config_parser.word_size
        elif current_byte < 86:
            commander.extra_cmd(current_byte, config_parser.config_zone_bin[current_byte])
            current_byte += 1
        elif current_byte < 88:
            # skip lock zone, should use lock single slot for 88-90 but also simple write works...
            current_byte += 2
        elif current_byte == 128:
            break

    return config_crc

@ateccx08a.command("write-config", help="write a configuration")
@click.argument("alias")
@click.argument("configuration_file", type=click.Path())
@click.option("--lock", default=False, type=bool)
def __write_config(alias, configuration_file, lock):
    cmd_ch = _serial_channel(alias)
    commander = SerialCommander(cmd_ch, info, fatal)

    desired_config = fs.get_yaml(configuration_file)
    for cmd, value in desired_config.items():
        config_parser.parse_cmd(cmd, value)

    config_crc = _do_write_config(commander)
    if lock:
        _do_lock(cmd_ch, config_crc)


@ateccx08a.command("get-csr", help="retrieve public key associated to private in chosen slot")
@click.argument("alias")
@click.argument("private_slot")
@click.argument("subject")
@click.option("--output", "-o", default='', type=click.Path())
def __get_csr(alias, private_slot, subject, output):
    cmd_ch = _serial_channel(alias)
    commander = SerialCommander(cmd_ch, info, fatal)
    csr = commander.get_csr(int(private_slot), subject)

    if output:
        if fs.is_dir(output):
            output=fs.path(output,"atecc.csr")
        fs.write_file(csr, output)
