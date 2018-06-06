# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2018-06-06 17:22:52
# @Last Modified by:   Lorenzo
# @Last Modified time: 2018-06-06 18:37:17

from .utils import *

class SerialCommander:

    def __init__(self, channel, out):
        self.cmd_ch = channel
        self.out = out

    def read_config(self):
        self.cmd_ch.write("readconfig\n")
        self.out("Read command sent")
        while True:
            line = self.cmd_ch.readline()
            if line == "ok\n":
                break
            self.out(line.strip("\n"))

    def get_public(self, private_slot):
        self.cmd_ch.write("getpublic "+str(private_slot)+"\n")
        key_len = self.cmd_ch.read(1)
        return self.cmd_ch.read(key_len[0])

    def getspecial_cmd(self):
        self.out('Getting Crypto Element Special Zone')
        self.cmd_ch.write(b'getspecial\n')
        specialzone = self.cmd_ch.ch.readline().strip(b'\n')[len('ok: '):]
        return specialzone

    def write_cmd(self, cb, bb):
        self.out('> write cmd:', word_fmt(cb, bb))
        self.cmd_ch.write(b'write ' + bytes([cb]) + bb + b'\n')
        self.out('>',self.cmd_ch.ch.readline().strip(b'\n').decode('utf-8'))

    def extra_cmd(self, cb, bb):
        self.out('> extra cmd:', cb, bb)
        self.cmd_ch.write(b'extra ' + bytes([cb,bb]) + b'\n')
        self.out('>',self.cmd_ch.ch.readline().strip(b'\n').decode('utf-8'))

    def lock_config_cmd(self, config_crc):
        self.out('> lock config cmd:', config_crc[0], config_crc[1])
        self.cmd_ch.write(b'lockconfig ' + config_crc + b'\n')
        self.out('>',self.cmd_ch.readline().strip(b'\n').decode('utf-8'))

    def lock_data_cmd(self):
        self.out('> lock data cmd')
        self.cmd_ch.write(b'lockdata\n')
        self.out('>',self.cmd_ch.readline().strip(b'\n').decode('utf-8'))

    def get_csr(self, private_slot, subject):
        self.cmd_ch.write("getcsr "+str(private_slot)+" "+ subject +"\n")
        self.cmd_ch.set_timeout(2)
        while True:
            line = self.cmd_ch.readline()
            if line == "ok\n":
                break
            self.out(line.strip("\n"))
        self.cmd_ch.set_timeout(0.5)
