from .base import *
import serial

__all__ = ["ConnectionInfo","Channel"]

class ConnectionInfo():

    PARITY = {
        "n":serial.PARITY_NONE,
        "e": serial.PARITY_EVEN,
        "m": serial.PARITY_MARK,
        "o": serial.PARITY_ODD,
        "s": serial.PARITY_SPACE,
    }

    STOPS = {
        1:serial.STOPBITS_ONE,
        1.5:serial.STOPBITS_ONE_POINT_FIVE,
        2:serial.STOPBITS_TWO
    }

    BITS = {
        5:serial.FIVEBITS,
        6:serial.SIXBITS,
        7:serial.SEVENBITS,
        8:serial.EIGHTBITS
    }

    def __init__(self):
        pass

    def is_serial(self):
        return self.type=="serial"

    def is_socket(self):
        return self.type=="socket"

    def set_serial(self,port,baudrate=115200,bytesize=8,parity=0,stopbits=1,dsrdtr=False, rtscts=False):
        self.type = "serial"
        self.port=port
        self.baudrate = baudrate
        self.bytesize = Connection.BITS[bytesize]
        self.parity = Connection.PARITY[parity]
        self.stopbits = Connection.STOPS[stopbits]
        self.dsrdtr = dsrdtr
        self.rtscts = rtscts

    def set_socket(self,ip,port):
        self.type="socket"
        self.ip = ip
        self.port = port


class ChannelException(Exception):
    def __init__(self,e):
        self.e=e

class Channel():
    def __init__(self,conn):
        self.conn = conn

    def open(self,timeout=None):
        try:
            self.timeout = timeout
            if self.conn.is_serial():
                self.ch = serial.Serial(self.conn.port,
                    baudrate=self.conn.baudrate,
                    bytesize=self.conn.bytesize,
                    stopbits=self.conn.stopbits,
                    parity=self.conn.parity,
                    dsrdtr=self.conn.dsrdtr,
                    rtscts=self.conn.rtscts,
                    timeout=self.timeout)
            else:
                pass
                #TODO: implement socket
        except serial.SerialException as se:
            raise ChannelException(se)
        except ValueError as ve:
            raise ChannelException(ve)

    def set_timeout(self,timeout):
        pass

    def write(self,data):
        self.ch.write(data)

    def read(self,n=1):
        return self.ch.read(n)

    def incoming(self):
        pass

    def flush(self):
        pass

    def close(self):
        pass

