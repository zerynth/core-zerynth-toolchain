# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2018-06-06 17:22:52
# @Last Modified by:   Lorenzo
# @Last Modified time: 2018-06-07 16:43:10

from .utils import *

raw_cmds = [
    'WCF', 'EXT', 'LCF', 'LDT', 'GSP', 'RCF', 'GPB', 'CSR'
]

WRITECFG_CMD   = 0
EXTRA_CMD      = 1
LOCKCFG_CMD    = 2
LOCKDATA_CMD   = 3
GETSPECIAL_CMD = 4
READCFG_CMD    = 5
GETPUBLIC_CMD  = 6
GETCSR_CMD     = 7

ASCII_RESP_CODE = 1
BIN_RESP_CODE   = 2

class SerialCommander:

    def __init__(self, channel, out, error):
        self.cmd_ch = channel
        self.out = out
        self.error = error

    def _exe_cmd(self, cmd_code, args=None):
        self.cmd_ch.write(raw_cmds[cmd_code])
        if args is not None:
            self.cmd_ch.write(bytes([len(args)]) + args)
        resp_type = self.cmd_ch.read(1)[0]
        resp_msg  = None
        resp_status  = None
        if resp_type == ASCII_RESP_CODE:
            resp_msg = ''
            while True:
                line = self.cmd_ch.readline()
                if line.startswith('ok: '):
                    resp_status = line.strip()
                    break
                elif line.startswith('exc'):
                    fatal('error executing command:', raw_cmds[cmd_code])
                resp_msg += line
        elif resp_type == BIN_RESP_CODE:
            resp_len = self.cmd_ch.read(1)[0]
            resp_msg = self.cmd_ch.read(resp_len)
        return resp_status, resp_msg

    def read_config(self):
        status, msg = self._exe_cmd(READCFG_CMD)
        self.out(" Read command sent\n", msg, sep='', end='')
        self.out(status)

    def get_public(self, private_slot):
        status, msg = self._exe_cmd(GETPUBLIC_CMD, bytes([private_slot]))
        return msg

    def getspecial_cmd(self):
        self.out('Getting Crypto Element Special Zone')
        status, specialzone = self._exe_cmd(GETSPECIAL_CMD)
        return specialzone

    def write_cmd(self, offset, bb):
        self.out('Write cmd:', word_fmt(offset, bb))
        status, msg = self._exe_cmd(WRITECFG_CMD, bytes([offset]) + bb)
        self.out(status)

    def extra_cmd(self, offset, bb):
        self.out('Extra cmd:', offset, bb)
        status, msg = self._exe_cmd(EXTRA_CMD, bytes([offset, bb]))
        self.out(status)

    def lock_config_cmd(self, config_crc):
        self.out('Lock config cmd:', config_crc[0], config_crc[1])
        status, msg = self._exe_cmd(LOCKCFG_CMD, config_crc)
        self.out(status)

    def lock_data_cmd(self):
        self.out('Lock data cmd')
        status, msg = self._exe_cmd(LOCKDATA_CMD)
        self.out(status)

    def get_csr(self, private_slot, subject):
        timeout = self.cmd_ch.get_timeout()
        self.cmd_ch.set_timeout(10)
        status, msg = self._exe_cmd(GETCSR_CMD, bytes([private_slot]) + subject.encode('ascii'))
        self.out('Certificate Request:\n', msg, end='')
        self.out(status)
        self.cmd_ch.set_timeout(timeout)
        return msg
