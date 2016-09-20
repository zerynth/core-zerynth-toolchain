from base import *

__all__=["Device","UsbToSerial","JTag","Board"]

class Device():
    def __init__(self,info={},dev={}):
        self._info=info
        self._dev = dev

    def hash(self):
        return self._info.get("shortname","---")+":"+self._dev.get("uid","---")

    def to_dict(self):
        x = {}
        x.update(self._info)
        x.update(self._dev)
        if "class" in x:
            del x["class"]
        if "cls" in x:
            del x["cls"]
        return x

    def __getattr__(self,attr):
        if attr!="class" and attr in self._info:
            return self._info[attr]
        if attr in self._dev:
            return self._dev[attr]
        raise AttributeError

    def virtualize(self,bin):
        pass

    def reset(self):
        pass

    def restore(self):
        pass


class UsbToSerial(Device):
    def __init__(self,info={},dev={}):
        super().__init__(info,dev)

class JTag(Device):
    def __init__(self,info={},dev={}):
        super().__init__(info,dev)

class Board(Device):
    def __init__(self,info={},dev={}):
        super().__init__(info,dev)







