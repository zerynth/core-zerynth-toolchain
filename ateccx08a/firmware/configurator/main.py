# ATcrypto_elementA_Configurator
# Created at 2018-04-27 08:41:51.023939

# TODO: do not pass arg bytes with commands, but only number of arg bytes, then args
#       do not pass resp bytes with ok, ...

import streams
import json
import threading

import x509
from microchip.ateccx08a import ateccx08a


csr_event = threading.Event()
last_csr  = None
csr_subject_str = None
def csr_thread():
    global last_csr
    while True:
        csr_event.wait()
        last_csr = x509.generate_csr_for_key('', csr_subject_str)
        csr_event.set()


def load_conf():
    confstream = open('resource://config.json')
    conf = ''
    while True:
        line = confstream.readline()
        if not line:
            break
        conf += line
    return json.loads(conf)

# debug channel
streams.serial(SERIAL2)

cmd_ch = streams.serial(set_default=False)

new_resource("config.json")
print('> load conf')
conf = load_conf()

print('> conf ok')

i2cdrv  = I2C0 + conf['i2cdrv']
i2caddr = conf['i2caddr']

print('> drv addr', i2cdrv, i2caddr)


def info_command_test():
    expected = bytes([0x00, 0x00, 0x50, 0x00])
    response = crypto_element.info_cmd('revision')
    return response == expected

config_zone_size = 127
word_size = 4

def word_fmt(word_addr, word):
    return ('%03d: ' % word_addr) + '-'.join([('%02X' % word_byte) for word_byte in word])

def out_config():
    for i in range((config_zone_size+1)//word_size):
        cmd_ch.write(word_fmt(i*word_size, crypto_element.read_cmd('Config', bytes([i*word_size>>2,0]), False)) + '\n')
    cmd_ch.write('ok\n')

def out_public(slot):
    public_key = crypto_element.gen_public_key_cmd(bytes([slot & 0xff, slot >> 8]), False, bytes(3))
    cmd_ch.write(bytes([len(public_key)]))
    cmd_ch.write(public_key)

def out_csr(slot, subject_str):
    global csr_subject_str
    ateccx08a.set_privatekey_slot(slot)
    csr_subject_str = subject_str
    csr_event.set()
    csr_event.wait()
    cmd_ch.write(last_csr + '\n')
    cmd_ch.write('ok\n')    

def btostr(mbytes, join_char='-'):
    return join_char.join([str(mbyte) for mbyte in mbytes])

def get_special():
    special = bytes()
    for i in range(4):
        special += crypto_element.read_cmd('Config', bytes([i,0]), False)
    return special

print('> init crypto')
crypto_element = ateccx08a.ATECC508A(i2cdrv, addr=i2caddr)
while not info_command_test():
    print('> cannot find ATECC508A')
    sleep(1000)
    crypto_element = ateccx08a.ATECC508A(i2cdrv, addr=i2caddr)

print('> init hwcrypto')
ateccx08a.hwcrypto_init(i2cdrv, 0, i2c_addr=i2caddr)
print('> hwcrypto ok')

thread(csr_thread, size=12288)

while True:

    print('> wait cmd')
    raw_cmd = cmd_ch.readline().strip('\n')

    try:
        if raw_cmd.startswith('write '):
            args = raw_cmd[6:] # len('write ')
            print('> write args:', btostr(args))
            err = crypto_element.write_cmd('Config', bytes([args[0]>>2, 0]), args[1:], False)
            print('> write ok')
            cmd_ch.write('ok: '+ btostr(err) + '\n')
        elif raw_cmd.startswith('extra '):
            args = raw_cmd[6:] # len('extra ')
            print('> extra args:', btostr(args))
            err = crypto_element.updateextra_cmd(args[0], args[1])
            cmd_ch.write('ok: ' + btostr(err) + '\n')
        elif raw_cmd.startswith('lockconfig '):
            args = raw_cmd[11:] # len('lockconfig ')
            checksum = bytes([args[0], args[1]])
            err = crypto_element.lock_config_zone_cmd(checksum=checksum)
            cmd_ch.write('ok: ' + btostr(err) + '\n')
        elif raw_cmd.startswith('lockdata'):
            err = crypto_element.lock_data_zone_cmd()
            cmd_ch.write('ok: ' + btostr(err) + '\n')
        elif raw_cmd.startswith('getspecial'):
            cmd_ch.write('ok: ' + get_special() + '\n')
        elif raw_cmd.startswith('readconfig'):
            out_config()
        elif raw_cmd.startswith('getpublic '):
            slot = int(raw_cmd[10:]) # 10 = len('getpublic ')
            out_public(slot)
        elif raw_cmd.startswith('getcsr '):
            slot_subject = raw_cmd[7:].split(' ') # 7 = len('getcsr ')
            slot = int(slot_subject[0]) 
            print('> get csr')
            out_csr(slot, slot_subject[1])
    except Exception as e:
        print(e)

