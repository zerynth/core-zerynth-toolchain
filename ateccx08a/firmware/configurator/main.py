# ATcrypto_elementA_Configurator
# Created at 2018-04-27 08:41:51.023939

# TODO: do not pass arg bytes with commands, but only number of arg bytes, then args
#       do not pass resp bytes with ok, ...

import streams
import json
import threading

import x509
from microchip.ateccx08a import ateccx08a


config_zone_size = 127
word_size = 4

def load_conf():
    confstream = open('resource://config.json')
    conf = ''
    while True:
        line = confstream.readline()
        if not line:
            break
        conf += line
    return json.loads(conf)

def word_fmt(word_addr, word):
    return ('%03d: ' % word_addr) + '-'.join([('%02X' % word_byte) for word_byte in word])


WRITECFG_CMD   = 0
EXTRA_CMD      = 1
LOCKCFG_CMD    = 2
LOCKDATA_CMD   = 3
GETSPECIAL_CMD = 4
READCFG_CMD    = 5
GETPUBLIC_CMD  = 6
GETCSR_CMD     = 7

raw_cmds = [
    'WCF', 'EXT', 'LCF', 'LDT', 'GSP', 'RCF', 'GPB', 'CSR'
]

has_args = [
    True, True, True, False, False, False, True, True
]

ASCII_RESP_CODE = 1
BIN_RESP_CODE   = 2

class CmdResponse:
    def __init__(self):
        self.reset()

    def reset(self):
        self.type   = None
        self.msg    = None
        self.status = None


class CommandHandler:
    def __init__(self, response_object):
        self.cmd_resp = response_object

        self._csr = None
        self._csr_subject_str = None
        self._csr_event = threading.Event()
        thread(self._csr_thread, size=12288)

    def write_cfg(self, offset, content):
        self.cmd_resp.status = crypto_element.write_cmd('Config', bytes([offset>>2, 0]), content, False)[0]
        self.cmd_resp.type   = ASCII_RESP_CODE

    def extra(self, b0, b1):
        self.cmd_resp.status = crypto_element.updateextra_cmd(b0, b1)[0]
        self.cmd_resp.type   = ASCII_RESP_CODE

    def lock_cfg(self, checksum):
        self.cmd_resp.status = crypto_element.lock_config_zone_cmd(checksum=checksum)[0]
        self.cmd_resp.type   = ASCII_RESP_CODE

    def lock_data(self):
        self.cmd_resp.status = crypto_element.lock_data_zone_cmd()[0]
        self.cmd_resp.type   = ASCII_RESP_CODE

    def get_special(self):
        special = bytes()
        for i in range(4):
            special += crypto_element.read_cmd('Config', bytes([i,0]), False)
        self.cmd_resp.msg  = special
        self.cmd_resp.type = BIN_RESP_CODE

    def get_public(self, slot):
        self.cmd_resp.msg  = crypto_element.gen_public_key_cmd(bytes([slot & 0xff, slot >> 8]), False, bytes(3))
        self.cmd_resp.type = BIN_RESP_CODE

    def out_config(self, channel):
        # keep cmd_resp.type None to notify progressive output (msg too big to be stored and eventually sent)
        channel.write(bytes([ASCII_RESP_CODE]))
        for i in range((config_zone_size+1)//word_size):
            channel.write(word_fmt(i*word_size, crypto_element.read_cmd('Config', bytes([i*word_size>>2, 0]), False)) + '\n')
        self.cmd_resp.status = 0

    def get_csr(self, slot, subject_str):
        ateccx08a.set_privatekey_slot(slot)
        self._csr_subject_str = subject_str
        self._csr_event.set()
        self._csr_event.clear()
        self._csr_event.wait()
        self.cmd_resp.msg  = self._csr
        self.cmd_resp.type = ASCII_RESP_CODE
        self.cmd_resp.status  = 0

    def _csr_thread(self):
        while True:
            self._csr_event.wait()
            self._csr = x509.generate_csr_for_key('', self._csr_subject_str)[:-1] # remove terminal 0
            self._csr_event.set()
            self._csr_event.clear()

# debug channel
streams.serial(SERIAL2)
# command channel
cmd_ch = streams.serial(set_default=False)

new_resource("config.json")
conf = load_conf()

i2cdrv  = I2C0 + conf['i2cdrv']
i2caddr = conf['i2caddr']

print('> init crypto')
crypto_element = ateccx08a.ATECC508A(i2cdrv, addr=i2caddr)
while crypto_element.info_cmd('revision') != b'\x00\x00\x50\x00':
    print('> cannot find ATECC508A')
    sleep(1000)
    crypto_element = ateccx08a.ATECC508A(i2cdrv, addr=i2caddr)

ateccx08a.hwcrypto_init(i2cdrv, 0, i2c_addr=i2caddr)
cmd_resp = CmdResponse()
command_handler = CommandHandler(cmd_resp)

while True:

    print('> wait cmd')
    raw_cmd = cmd_ch.read(3) # read command code
    raw_cmd_code = None
    cmd_resp.reset()
    print('> raw_cmd', raw_cmd)

    for rcmd_code, rcmd in enumerate(raw_cmds):
        if rcmd == raw_cmd:
            raw_cmd_code = rcmd_code
            break
    else:
        continue

    print('> code', raw_cmd_code)
    if has_args[raw_cmd_code]:
        args_len = cmd_ch.read(1)[0] # number of args bytes
        args = cmd_ch.read(args_len)

    try:
        if raw_cmd_code == WRITECFG_CMD:
            print('> write args:', word_fmt(args[0], args[1:]))
            command_handler.write_cfg(args[0], args[1:])
        elif raw_cmd_code == EXTRA_CMD:
            print('> extra args: ', args[0], '-', args[1])
            command_handler.extra(args[0], args[1])
        elif raw_cmd_code == LOCKCFG_CMD:
            command_handler.lock_cfg(args[:1])
        elif raw_cmd_code == LOCKDATA_CMD:
            command_handler.lock_data()
        elif raw_cmd_code == GETSPECIAL_CMD:
            command_handler.get_special()
        elif raw_cmd_code == READCFG_CMD:
            command_handler.out_config(cmd_ch)
        elif raw_cmd_code == GETPUBLIC_CMD:
            command_handler.get_public(args[0])
        elif raw_cmd_code == GETCSR_CMD:
            command_handler.get_csr(args[0], args[1:])

        if cmd_resp.type is not None:
            cmd_ch.write(bytes([cmd_resp.type])) # write a single byte to notify resp mode

        if cmd_resp.type == BIN_RESP_CODE:
            cmd_ch.write(bytes([len(cmd_resp.msg)]))

        if cmd_resp.msg:
            print('> write msg')
            cmd_ch.write(cmd_resp.msg)

        if cmd_resp.type == ASCII_RESP_CODE or cmd_resp.type is None:
            print('> write err')
            cmd_ch.write('ok: '+ hex(cmd_resp.status) + '\n')

    except Exception as e:
        cmd_ch.write(ASCII_RESP_CODE)
        cmd_ch.write('exc\n')
        print(e)

