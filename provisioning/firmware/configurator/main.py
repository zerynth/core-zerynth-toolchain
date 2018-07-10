# ATECCx08A_Configurator
# Created at 2018-04-27 08:41:51.023939

import streams
import json
import threading

import x509
from microchip.ateccx08a import ateccx08a

config_zone_size = 128
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
GENPRIVATE_CMD = 8
GETLOCKED_CMD  = 9
GETSERNUM_CMD  = 10
SCANCRYPTO_CMD = 11

raw_cmds = [
    'WCF', 'EXT', 'LCF', 'LDT', 'GSP', 'RCF', 'GPB', 'CSR', 'GPV', 'GLK', 'GSN', 'SCN'
]

has_args = [
    True, True, True, False, False, False, True, True, True, False, False, False
]

ASCII_RESP_CODE = 1
BIN_RESP_CODE   = 2

class CryptoInfo:
    def __init__(self, drv, addr, plugged):
        self.drv = drv
        self.addr = addr
        self.plugged = plugged


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
        self.cmd_resp.msg  = crypto_element.gen_public_key(slot)
        self.cmd_resp.type = BIN_RESP_CODE

    def generate_private(self, slot):
        self.cmd_resp.msg  = crypto_element.gen_private_key(slot)
        self.cmd_resp.type = BIN_RESP_CODE

    def get_locked(self):
        locked_config = crypto_element.is_locked('Config')
        locked_data   = crypto_element.is_locked('Data')
        locked_config = {'Config': locked_config, 'Data': locked_data}
        self.cmd_resp.msg  = json.dumps(locked_config) + '\n'
        self.cmd_resp.type = ASCII_RESP_CODE
        self.cmd_resp.status = 0

    def get_serial_number(self):
        self.cmd_resp.msg  = crypto_element.serial_number()
        self.cmd_resp.type = BIN_RESP_CODE

    def out_config(self, channel):
        # keep cmd_resp.type None to notify progressive output (msg too big to be stored and eventually sent)
        channel.write(bytes([ASCII_RESP_CODE]))
        for i in range((config_zone_size)//word_size):
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

    def scan_crypto(self):
        if crypto_info.plugged:
            self.cmd_resp.msg = crypto_info.addr
            self.cmd_resp.type = BIN_RESP_CODE
            return

        for addr in range(0x100):
            crypto_element_init(addr)
            try:
                if crypto_element.info_cmd('revision') == b'\x00\x00\x50\x00':
                    crypto_info.addr = addr
                    crypto_info.plugged = True
                    break
            except Exception:
                pass
            sleep(20)
        if crypto_info.addr != -1:
            ateccx08a.hwcrypto_init(crypto_info.drv, 0, i2c_addr=crypto_info.addr)
            self.cmd_resp.msg = bytes([crypto_info.addr])
            self.cmd_resp.type = BIN_RESP_CODE
        else:
            self.cmd_resp.msg = bytes([0])
            self.cmd_resp.type = BIN_RESP_CODE

def crypto_element_init(addr):
    global crypto_element
    crypto_element = ateccx08a.ATECC508A(crypto_info.drv, addr=addr)

# debug channel
# streams.serial(SERIAL1)
# command channel
cmd_ch = streams.serial(set_default=False)

new_resource("config.json")
conf = load_conf()

crypto_info = CryptoInfo(I2C0 + conf['i2cdrv'], conf['i2caddr'], False)

cmd_resp = CmdResponse()
command_handler = CommandHandler(cmd_resp)

discover_retries = 0
crypto_element   = None

while True:
    try:
        crypto_element_init(crypto_info.addr)
        if crypto_element.info_cmd('revision') == b'\x00\x00\x50\x00':
            crypto_info.plugged = True
            break
    except Exception:
        pass
    if discover_retries > 5:
        break
    discover_retries += 1
    sleep(100)

if crypto_info.plugged:
    ateccx08a.hwcrypto_init(crypto_info.drv, 0, i2c_addr=crypto_info.addr)
else:
    crypto_info.addr = -1

while True:

    # print('> wait cmd')
    try:
        raw_cmd = cmd_ch.readline().strip('\n') # read command code
    except Exception as e:
        continue

    if len(raw_cmd) != 3:
        cmd_ch.write('notvalidcmd\n')
        continue

    # print('> read cmd')
    raw_cmd_code = None
    cmd_resp.reset()
    # print('> raw_cmd', raw_cmd)

    for rcmd_code, rcmd in enumerate(raw_cmds):
        if rcmd == raw_cmd:
            raw_cmd_code = rcmd_code
            break
    else:
        cmd_ch.write('notvalidcmd\n')
        continue

    cmd_ch.write('acceptedcmd\n')
    # print('> code', raw_cmd_code)
    if has_args[raw_cmd_code]:
        args_len = cmd_ch.read(1)[0] # number of args bytes
        args = cmd_ch.read(args_len)

    try:
        if raw_cmd_code == WRITECFG_CMD:
            # print('> write args:', word_fmt(args[0], args[1:]))
            command_handler.write_cfg(args[0], args[1:])
        elif raw_cmd_code == EXTRA_CMD:
            # print('> extra args: ', args[0], '-', args[1])
            command_handler.extra(args[0], args[1])
        elif raw_cmd_code == LOCKCFG_CMD:
            command_handler.lock_cfg(args[:2])
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
        elif raw_cmd_code == GENPRIVATE_CMD:
            command_handler.generate_private(args[0])
        elif raw_cmd_code == GETLOCKED_CMD:
            command_handler.get_locked()
        elif raw_cmd_code == GETSERNUM_CMD:
            command_handler.get_serial_number()
        elif raw_cmd_code == SCANCRYPTO_CMD:
            command_handler.scan_crypto()

        if cmd_resp.type is not None:
            cmd_ch.write(bytes([cmd_resp.type])) # write a single byte to notify resp mode

        txmsg = b''
        if cmd_resp.type == BIN_RESP_CODE:
            txmsg += bytes([len(cmd_resp.msg)])

        if cmd_resp.msg:
            txmsg += cmd_resp.msg

            # building and sending all at once because sending len first, then msg caused problems 
            # on some devices (e.g. particle_photon)
            cmd_ch.write(txmsg)

        if cmd_resp.type == ASCII_RESP_CODE or cmd_resp.type is None:
            # print('> write err')
            cmd_ch.write('ok: '+ hex(cmd_resp.status) + '\n')

    except Exception as e:
        cmd_ch.write(ASCII_RESP_CODE)
        cmd_ch.write('exc\n')
        # print(e)

