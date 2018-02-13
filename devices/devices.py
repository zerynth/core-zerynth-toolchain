from base import *
import re

__all__=["Device","Board"]

class Device():
    def __init__(self,info={},dev={}):
        self._info=info
        self._dev = dev
        self._info["classname"] = self.__class__.__name__

    def hash(self):
        return self._info.get("target","---")+":"+self._dev.get("uid","---")

    def to_dict(self):
        x = {}
        x.update(self._info)
        x.update(self._dev)
        if "class" in x:
            x["classes"]=x["class"]
            del x["class"]
        if "cls" in x:
            del x["cls"]
        return x
        
    def __getitem__(self,key):
        return self.__getattr__(key)


    def __getattr__(self,attr):
        if attr in self._info:
            return self._info[attr]
        if attr in self._dev:
            return self._dev[attr]
        return None
        #raise AttributeError ##TODO: check correctness

    def get(self,attr,default=None):
        x = self.__getattr__(attr)
        if x is None: return default
        return x

    def set(self,attr,value):
        self._dev[attr]=value

    def virtualize(self,bin):
        pass

    def reset(self):
        pass

    def restore(self):
        pass

    def load_family(self):
        dpath = fs.path(env.vhal,self.family_type,self.family_name,"vhal.json")
        try:
            self.family = fs.get_json(dpath)
            return True
        except Exception as e:
            warning("Can't load device family!",self.family_name,"@",dpath)
        return False


    def load_specs(self):
        try:
            defines, peripherals, pinout = self.__get_specs()
            names = set()
            for k,v in pinout.items():
                names.add(k)
                for z,w in v.items():
                    names.add(w)
            names.update(peripherals)
            self.defines = defines
            self.peripherals=peripherals
            self.pinmap=pinout
            self.names=names

            classes = {
                "D":0x0000,
                "A":0x0100,
                "SPI":0x0200,
                "I2C":0x0300,
                "PWM":0x0400,
                "ICU":0x0500,
                "CAN":0x0600,
                "SER":0x0700,
                "DAC":0x0800,
                "LED":0x0900,
                "BTN":0x0A00
            }
            vcls = {
               "SPI":["MOSI","MISO","SCLK"],
                "I2C":["SDA","SCL"],
                "SER":["RX","TX"],
                "CAN":["CANRX","CANTX"]
            }
            prphs = {
                "SERIAL":0x700,
                "SPI":0x0200,
                "I2C":0x0300,
                "ADC":0x0100,
                "PWMD":0x0400,
                "ICUD":0x0500,
                "CAN":0x0600,
                "SD":0x0B00
            }

            # build dictionary with all valid pin names and prph names
            self.allnames = {}
            for k,v in classes.items():
                if k in vcls:
                    lst =vcls[k]
                    for x in range(0,128):
                        kname = lst[x%len(lst)]+str(x//len(lst))
                        kvalue = classes[k]+x
                        if kname in self.names:
                            self.allnames[kname]=kvalue
                else:
                    for x in range(0,128):
                        kname = k+str(x)
                        kvalue = classes[k]+x
                        if kname in self.names:
                            self.allnames[kname]=kvalue

            for k,v in prphs.items():
                for x in range(0,32):
                    kname = k+str(x)
                    kvalue = v+x
                    if kname in self.names:
                        self.allnames[kname]=kvalue
        except Exception as e:
            raise e

    def __get_specs(self):
        portfile = fs.path(self.path,"port","port.def")

        with open(portfile,"r") as ff:
            lines = ff.readlines()

        mth_list = re.compile('////(.*): (.*)')
        mth_pin = re.compile('\s*/\*\s*([DA0-9]*)\s.*\*/\s*MAKE_PIN\(')
        mth_cls = re.compile('.*MAKE_PIN_CLASS\(([0-9]*),')
        mth_header = re.compile('.*\sconst\s*_(.*)class\[\]\s*STORED')

        names = {
            "SPI":["MOSI","MISO","SCLK"],
            "I2C":["SDA","SCL"],
            "SER":["RX","TX"],
            "CAN":["CANRX","CANTX"],
            "PWM":["PWM"],
            "ICU":["ICU"],
            "ADC":["A"],
            "DAC":["DAC"],
        }

        vpins = {}
        vnames = {}
        vlayout = []
        vprph = []
        cdefs = []

        cfun = None
        clsc = 0
        npin = 0
        for line in lines:
            mth = mth_list.match(line)
            if mth:
                if mth.group(1)=="LAYOUT":
                    vlayout = mth.group(2).strip().split(" ")
                elif mth.group(1)=="PERIPHERALS":
                    vprph = mth.group(2).strip().split(" ")
                elif mth.group(1)=="CDEFINES":
                    cdefs.extend(mth.group(2).strip().split(" "))
                continue
            mth = mth_pin.match(line)
            if mth:
                #print("matched p",line)
                pname = mth.group(1)
                pidx = npin
                if pidx not in vpins:
                    vpins[pidx] = {
                        "name":pname,
                        "idx":pidx,
                        "fx":{}
                    }
                npin+=1
            else:
                mth = mth_header.match(line)
                if mth:
                    #print("matched h",line)
                    cfun = mth.group(1).upper()
                    clsc = 0
                else:
                    mth = mth_cls.match(line)
                    if mth:
                        #print("matched c",line)
                        pidx = int(mth.group(1))
                        pin = vpins[pidx]
                        if cfun=="DIGITAL":
                            continue
                        if cfun=="ANALOG":
                            cfun="ADC"

                        if cfun in ["LED","BTN"]:
                            vnames[cfun+str(clsc)]=pidx
                        elif cfun not in pin["fx"]:
                            lst = names[cfun]
                            if len(lst)>1:
                                pin["fx"][lst[clsc%len(lst)]]=lst[clsc%len(lst)]+str(clsc//len(lst))
                            else:
                                pin["fx"][cfun]=lst[0]+str(clsc)
                        clsc+=1

        #import pprint
        import collections

        #pp = pprint.PrettyPrinter(indent=4)


        pinout = collections.OrderedDict()
        lpins = [v for k,v in vpins.items()]
        lpins.sort(key= lambda x: x["idx"])

        for lpin in lpins:
            pinout[lpin["name"]]=lpin["fx"]

        for vname in vnames:
            pinout[vname]=vpins[vnames[vname]]["fx"]

        defines = {
            "BOARD": self.target,
            "LAYOUT": vlayout,
            "CDEFS": cdefs
        }

        return (defines,vprph,pinout)

class Board(Device):
    def __init__(self,info={},dev={}):
        super().__init__(info,dev)







