# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2018-05-03 16:32:55
# @Last Modified by:   Lorenzo
# @Last Modified time: 2018-06-07 15:47:42


from .ecdsa.util import oid_ecPublicKey, encoded_oid_ecPublicKey
from .ecdsa import NIST256p, der

import binascii

def to_der(curve, x, y):
    point_str = b"\x00\x04" + x + y
    return der.encode_sequence(der.encode_sequence(encoded_oid_ecPublicKey, curve.encoded_oid),
                               der.encode_bitstring(point_str))

def to_pem(curve, x, y):
    return der.topem(to_der(curve, x, y), "PUBLIC KEY")

def xytopem(xy):
    x, y = xy[:32], xy[32:]
    return to_pem(NIST256p, x, y).decode('utf-8')

def xytohex(xy):
    return '0x' + binascii.hexlify(xy).decode('utf-8')