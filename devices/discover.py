from base import *
import sys
import importlib
import json
import hashlib



__all__=['Discover']



class Discover():
    def __init__(self):
        self.round=0
        if env.is_unix():
            self.devstrings={
                "ID_SERIAL":"serial",
                "ID_SERIAL_SHORT":"sid",
                "ID_VENDOR_ID":"vid",
                "ID_MODEL_ID":"pid",
                "SUBSYSTEM":"sys",
                "DEVNAME":"dev"
            }
            import pyudev
            self.devkeys = set(self.devstrings.keys())
            self.udev = pyudev.Context()
        self.devices = {}
        self.matched_devices = {}
        self.device_cls = {}
        self.targets = {}
        self.load_devices()

    def get_targets(self):
        return self.targets

    def get_target(self,target):
        tgt = self.targets[target]
        return tgt["cls"](tgt,{}) 

    def load_devices(self):
        bdirs = fs.dirs(env.devices)
        for bdir in bdirs:
            try:
                bj = fs.get_json(fs.path(bdir,"device.json"))
                bj["path"] = bdir
                for cls in bj["class"]:
                    try:
                        sys.path.append(bdir)
                        module,bcls = cls.split(".")
                        bc = importlib.import_module(module)
                        dcls = getattr(bc,bcls)
                        bjc = dict(bj)
                        bjc["cls"]=dcls
                        sys.path.pop()
                        self.device_cls[bdir+"::"+bcls]=bjc
                        if "target" in bj:
                            self.targets[bj["target"]]=bjc
                    except Exception as e:
                        warning(e,err=True)
            except Exception as e:
                warning(e,err=True)

    def wait_for_uid(self,uid,loop=5,matchdb=True):
        for l in range(loop):
            devs = self.run_one(matchdb)
            uids = self.matching_uids(devs,uid)
            if len(uids)>=1:
                return uids,devs
            sleep(1)
            info("attempt",l+1)
        return [],{}


    def parse(self):
        if env.is_windows():
            self.parse_windows()
        elif env.is_mac():
            self.parse_mac()
        else:
            return self.parse_linux()

    def output_devices(self,pretty=False):
        indent = 4 if pretty else None
        if not self.devices:
            log(" ")
        else:
            for k,v in self.devices.items():
                log(json.dumps(v,indent=indent))
        log("")

    def output_matched_devices(self,pretty=False):
        indent = 4 if pretty else None
        if not self.matched_devices:
            log(" ")
        else:
            for k,v in self.matched_devices.items():
                dd = v.to_dict()
                dd["hash"]=k
                log(json.dumps(dd,indent=indent))
        log("")

    def compare_dbs(self, new_db, old_db):
        if new_db.keys()!=old_db.keys():
            return False
        else:
            for k,v in old_db.items():
                if new_db[k]["fingerprint"]!=v["fingerprint"]:
                    return False
        return True

    def match_devices(self):
        ndb = {}
        pdevs = []
        tuid= {}
        # augment devices with devdb info (alias and target and name)
        for uid,dev in self.devices.items():
            devs = env.get_dev(uid)
            if devs:
                for alias,d in devs.items():
                    x = dict(dev)
                    x["alias"] = d.alias
                    x["custom_name"] = d.name
                    x["target"] = d.target
                    x["chipid"] = d.chipid
                    x["remote_id"] = d.remote_id
                    pdevs.append(x)
                    if d.uid not in tuid:
                        tuid[d.uid]=[]
                    tuid[d.uid].append(x)
            else:
                dev["alias"]=None
                pdevs.append(dev)
        
        # perform device - known device matching
        for dkey,dinfo in self.device_cls.items():
            cls = dinfo["cls"]
            for dev in pdevs:
                #print("Checking",dev["uid"],dev["uid"] in tuid,dev)
                if dev["uid"] in tuid:  # uid with alias and target
                    if dinfo.get("target")==dev.get("target","-"):
                        obj = cls(dinfo,dev)
                        ndb[obj.hash()]=obj
                elif cls.match(dev):
                    obj = cls(dinfo,dev)
                    ndb[obj.hash()]=obj
        return ndb

    def matching_uids(self,devs,a_uid):
        uids=[]
        for uid,dev in devs.items():
            u = dev.uid
            if u.startswith(a_uid):
                uids.append(u)
        return uids


    def matching_uids_or_alias(self,devs,a_uid):
        uids=[]
        for uid,dev in devs.items():
            if dev.uid.startswith(a_uid):
                uids.append(dev.uid)
            elif dev.alias and dev.alias.startswith(a_uid):
                uids.append(dev.alias)
        return uids

    def get_by_alias(self,devs,alias):
        for h,dev in devs.items():
            if dev.alias==alias:
                return dev
        return None

    def find_again(self,dev):
        uids,devs = self.wait_for_uid(dev.uid)
        if len(uids)!=1:
            return None
        return devs[dev.hash()]



    def search_for_device(self,alias):
        devs = self.run_one(True)
        res = []
        for h,dev in devs.items():
            if dev.alias==alias:
                return dev
            elif dev.alias.startswith(alias):
                res.append(dev)
        if len(res)==1:
            return res[0]
        return res


    def run_one(self,matchdb):
        nd = self.parse()
        if matchdb:
            self.devices=nd
            return self.match_devices()
        else:
            return nd

    def run(self,loop,looptime,matchdb,pretty):
        while True:
            show=False

            # parse devices
            nd = self.parse()
            if not self.compare_dbs(nd,self.devices):
                self.devices=nd
                show=True

            if matchdb and show:
                self.matched_devices = self.match_devices()
                self.output_matched_devices(pretty)
            elif show:
                self.output_devices(pretty)

            if loop: 
                sleep(looptime)
            else:
                break
        

    def make_uid(self,dev):
        h = hashlib.sha1()
        k = dev["vid"]+":"+dev["pid"]+":"+dev["sid"]
        h.update(bytes(k,"ascii"))
        return h.hexdigest()

    def make_fingerprint(self,dev):
        return (dev["port"] or "")+":"+(dev["disk"] or "")


############ LINUX

    def find_mount_point(self,block):
        if not block:
            return
        e,out,err = proc.run("mount -v")
        if not e:
            lines = out.split("\n")
            for line in lines:
                if line.startswith(block):
                    flds = line.split(" ")
                    if len(flds)>=4 and flds[0]==block and flds[1]=="on" and flds[3]=="type":
                        return flds[2]

    def parse_linux(self):
        newdevices={}
        for device in self.udev.list_devices():
            try:
                if "SUBSYSTEM" in device and device["SUBSYSTEM"] in ("block","tty","usb"):
                    if self.devkeys.issubset(device):
                        dev={
                            "vid":device["ID_VENDOR_ID"].upper(),
                            "pid":device["ID_MODEL_ID"].upper(),
                            "sid":device["ID_SERIAL_SHORT"].upper(),
                            "port": device["DEVNAME"] if device["SUBSYSTEM"] == "tty" else None,
                            "block": device["DEVNAME"] if device["SUBSYSTEM"] == "block" else None,
                            "disk": self.find_mount_point(device["DEVNAME"]) if device["SUBSYSTEM"] == "block" else None,
                            "desc": device["ID_SERIAL"]
                        }
                        dev["uid"]=self.make_uid(dev)
                        dev["fingerprint"]=self.make_fingerprint(dev)
                        if dev["uid"] not in newdevices:
                            newdevices[dev["uid"]]={}
                        newdevices[dev["uid"]][dev["fingerprint"]]=dev
            except Exception as e:
                print("#",e)
        #fuse devices by uid
        ret={}
        for k,v in newdevices.items():
            fused = {}
            for fg,vv in v.items():
                for key,value in vv.items():
                    if (key not in fused) or not fused[key]:
                        fused[key]=value
            fused["fingerprint"]=self.make_fingerprint(fused)
            ret[k]=fused
        return ret
        



# class ViperListener(ViperThread):
#     def __init__(self):
#         super().__init__()
#         self.boards_plugged={}
#         self.fresh_boards = True
#         self.devices = {}
#         self.b_lock = threading.Lock()
#         if vconf.platform=="linux":
#             self.runfn=self.run_linux
#             self.setupfn=self.setup_linux
#             self.stopfn=self.stop_linux
#         elif vconf.platform=="windows":
#             self.runfn=self.run_win
#             self.setupfn=self.setup_win
#             self.stopfn=self.stop_win
#         elif vconf.platform=="mac":
#             self.runfn=self.run_mac
#             self.setupfn=self.setup_mac
#             self.stopfn=self.stop_mac
#             self.load_boards()

#     def load_boards(self):
#         tb.reload_boards()
#         self.vendors = {}
#         self.models = set()
#         self.board_by_vendor = {}
#         for board in tb.boards:
#             if hasattr(board,"ids_vendor"):
#                 for x in board.ids_vendor:
#                     if x not in self.vendors:
#                         self.vendors[x]=set()
#                     self.vendors[x].update(board.ids_vendor[x])
#                     if x not in self.board_by_vendor:
#                         self.board_by_vendor[x]=set()
#                     self.board_by_vendor[x].add(board)
#         print(self.vendors)

#     def get_boards(self):
#         self.b_lock.acquire()
#         self.boards_plugged=[]
#         self.boards_unplugged=[]
#         for brd in tb.boards:
#             bb = brd.discover(self.devices)
#             if bb:
#                 self.boards_plugged.extend(bb)
#             else:
#                 if not hasattr(brd,"not_virtual"):
#                     bbb = brd({"port":"X","disk":"X","uid":brd.board+"_"+brd.__name__+"_virtual_","vendor":"0000","model":"0000","devstring":"X"})
#                     self.boards_unplugged.append(bbb)

#         # check plugged for multiple choiches
#         plugged_uids = {}
#         for plugged in self.boards_plugged:
#             if not plugged.uid in plugged_uids:
#                 plugged_uids.update({ plugged.uid: [plugged] })
#             else:
#                 plugged_uids[plugged.uid].append(plugged)
#         for uid,m_brds in plugged_uids.items():
#             if len(m_brds) > 1:
#                 # multiple match, check association file
#                 ass_file = os.path.join(vconf.envdirs["devices"],uid)
#                 ass_found = False
#                 if os.path.exists(ass_file):
#                     with open(ass_file,"r") as ff:
#                         ass_board = json.load(ff)

#                     if "board" in ass_board:
#                         ass_found = True
#                         # already made association, leave only associated plugged board
#                         # read device name and check with brd.board
#                         unplug = []
#                         for n_brd in self.boards_plugged:
#                             if n_brd.uid == uid:
#                                 if n_brd.board == ass_board["board"]:
#                                     n_brd.associated = True
#                                 else:
#                                     unplug.append(n_brd)

#                         for ug in unplug:
#                             self.boards_plugged.remove(ug)

#                             brd = ug.__class__
#                             if not hasattr(brd,"not_virtual"):
#                                 bbb = brd({"port":"X","disk":"X","uid":brd.board+"_"+brd.__name__+"_virtual_","vendor":"0000","model":"0000","devstring":"X"})
#                             self.boards_unplugged.append(bbb)

#                 if not ass_found:
#                     # notify
#                     for i,m_brd in enumerate(m_brds):
#                         m_brd.uid = m_brd.uid + "_ASS_N_" + str(i)

#         plgd = {x.uid:x for x in self.boards_plugged}
#         uplg = {x.uid:x for x in self.boards_unplugged}
#         self.fresh_boards=False
#         self.b_lock.release()
#         return (plgd,uplg)
#     def refresh(self):
#         self.b_lock.acquire()
#         tb.reload_boards()
#         self.b_lock.release()
#     def start(self):
#         self._start(self.run,"Device Listener")
#     def run(self):
#         self.setupfn()
#         while self.running:
#             self.runfn()
#         self.stopfn
#     def _make_uid(self,vid,pid,sid):
#         return vid.upper()+"_"+pid.upper()+"_"+sid.upper()

# ######################################## LINUX
#     def setup_linux(self):
#         self.keys = frozenset(["ID_SERIAL","ID_SERIAL_SHORT","ID_VENDOR_ID","ID_MODEL_ID","SUBSYSTEM","DEVNAME"])
#         self.context = pyudev.Context()
#         logger.info("Listing all devices")
#         for device in self.context.list_devices():
#             if device["SUBSYSTEM"] in ("block","tty","usb"):
#                 uid, dev = self.check_dev_linux(device)
#                 if uid:
#                     self.b_lock.acquire()
#                     self.devices[uid]=dev
#                     self.fresh_boards=True
#                     self.b_lock.release()

#         logger.info("Creating UDEV Monitor")
#         self.monitor = pyudev.Monitor.from_netlink(self.context)
#         self.monitor.filter_by("tty")
#         self.monitor.filter_by("block")
#         self.monitor.filter_by("usb")
#         self.monitor.start()
#     def stop_linux(self):
#         pass
#     def check_dev_linux(self,dev,action="add"):
#         uid=""
#         device = {}
#         if self.keys.issubset(dev):
#             uid = self._make_uid(dev["ID_VENDOR_ID"],dev["ID_MODEL_ID"],dev["ID_SERIAL_SHORT"])
#             print("UID: ",uid)
#             if uid in self.devices:
#                 device=self.devices[uid]
#             else:
#                 device={}
#                 for kk,dd in self.devices.items():
#                     if dd.get("serial","")==dev["ID_SERIAL_SHORT"]:
#                         device=dd
#                         break
#             print("DEVICE",device,dev)
#             if device and action=="remove":
#                 return (uid,device)
#             if "serial" not in device:
#                 device["serial"]=dev["ID_SERIAL_SHORT"]
#             if "devstring" not in device:
#                 device["devstring"]=dev["ID_SERIAL"]
#             if "vendor" not in device:
#                 device["vendor"]=dev["ID_VENDOR_ID"].upper()
#             if "model" not in device:
#                 device["model"]=dev["ID_MODEL_ID"].upper()
#             if "uid" not in device:
#                 device["uid"] = uid
#             if dev["SUBSYSTEM"]=="tty":
#                 device["port"]=  dev["DEVNAME"]
#             elif dev["SUBSYSTEM"]=="block":
#                 block = dev["DEVNAME"]
#                 # if device["vendor"] in self.vendors and device["model"] in self.vendors[device["vendor"]]:
#                     #go on and check mount points
#                     # pass
#                 # else:
#                     # return ("",{})
#                 attempts=0
#                 while action=="add":
#                     ret,out = tb.runcmd("mount","-v")
#                     logger.info("Checking mount points for %s",uid)
#                     device["disk"]=""
#                     if not ret:
#                         paths = out.split("\n")
#                         for path in paths:
#                             words = path.split()
#                             if len(words)>=4: 
#                                 #Mmm...what if there are spaces in the path name!?!
#                                 if words[0].startswith(block) and words[1]=="on" and words[3]=="type":
#                                     if words[0]==block:
#                                         device["disk"]=words[2]
#                                         logger.info("FOUND!!! %s = %s",block,device["disk"])
#                                         break
#                                     else:
#                                         #since it startswith, it has partitions..ignore it and go to next device
#                                         return ("",{})
#                     if device["disk"]:
#                         break
#                     else:
#                         time.sleep(1)
#                         attempts+=1
#                         if attempts>10:
#                             return ("",{})
#         return(uid,device)
#     def run_linux(self):
#         dev = self.monitor.poll(5)
#         if dev:
#             uid,device = self.check_dev_linux(dev,dev.action)
#             if uid:
#                 if dev.action=="remove" and uid in self.devices:
#                     del self.devices[uid]
#                 elif dev.action=="add":
#                     self.devices[uid]=device
#                 logger.info("DEVICE (%s): %s",dev.action,device["uid"])
#                 self.b_lock.acquire()
#                 self.fresh_boards=True
#                 self.b_lock.release()

# ######################################## WINDOWS
#     def setup_win(self):
#         self.smth = re.compile("USB\\\\(?:[^\\\\]*&)*VID_([0-9a-fA-F]*)&PID_([0-9a-fA-F]*)(?:&[^\\\\]*)*\\\\([^\\\\]*)")
#         self.hmth = re.compile('.*="(.*)"')
#         self.devices = {}
#         pythoncom.CoInitialize()
#         self.wmic = win32com.client.GetObject ("winmgmts:")
#         self.wmi = wmi.WMI()
#     def stop_win(self):
#         pythoncom.CoUninitialize()
#     def check_dev_win(self,dev,action="add"):
#         pass
#     def _get_win_device_id(self,pnp):
#         mth =self.smth.match(pnp)
#         if mth:
#             return (
#                 mth.group(1).upper(),
#                 mth.group(2).upper(),
#                 mth.group(3).upper(),
#                 self._make_uid(mth.group(1),mth.group(2),mth.group(3))
#                 )
#         return (None,None,None,None)
#     def _split_sid(self,sid):
#         if "&" in sid:
#             return sid.split("&")[1]
#         return None
#     def _get_hw_specs(self):
#         pnps = {}
#         curpnp = None
#         curvid = None
#         curpid = None
#         for usb in self.wmi.InstancesOf ("Win32_USBControllerDevice"):
#             mth = self.hmth.match(usb.Dependent)
#             if mth:
#                 unescaped = bytes(mth.group(1),"utf-8").decode('unicode_escape')
#                 vid,pid,sid,uid = self._get_win_device_id(unescaped)
#                 if vid:
#                     if "&" in sid:
#                         #not a device spec, get instance id code
#                         iid = self._split_sid(sid)
#                         if curpnp and vid==curvid and pid==curpid:
#                             pnps[curpnp].add(iid)
#                     else:
#                         if curpnp!=sid:
#                             pnps[sid]=set()
#                             curpnp=sid
#                             curvid=vid
#                             curpid=pid
#         return pnps
#     def _get_hw(self,sids=[],nouids=[]):
#         pnps = {}
#         curpnp=None
#         for usb in self.wmi.InstancesOf ("Win32_PNPEntity"):
#             #unescaped = bytes(usb.PNPDeviceID,"utf-8").decode('unicode_escape')
#             vid,pid,sid,uid = self._get_win_device_id(usb.PNPDeviceID)
#             if uid and uid not in nouids and sid in sids:
#                 #print("HW==>",uid)
#                 if curpnp!=sid:
#                     pnps[sid]=usb
#                     curpnp=sid
#         return pnps
#     def _get_drive_letter_from_id(self,sid):
#         for physical_disk in self.wmi.Win32_DiskDrive (InterfaceType="USB"):
#             for partition in physical_disk.associators ("Win32_DiskDriveToDiskPartition"):
#                 for logical_disk in partition.associators ("Win32_LogicalDiskToPartition"):
#                     if sid in physical_disk.PNPDeviceID:
#                         return logical_disk.DeviceID
#         return ""
#     def run_win(self):
#         self.cdevs={}
#         dfnd = set()
#         time.sleep(1)
#         pnps = self._get_hw_specs()
#         serdev =[]
#         #print("PNPS=>",pnps)
#         for x in self.wmi.Win32_SerialPort():
#             vid,pid,sid,uid = self._get_win_device_id(x.PNPDeviceID)
#             if sid:
#                 ddisk=""
#                 if sid in pnps:
#                     #it's a non composite usb serial device
#                     pass
#                 else:
#                     #it's a composite device, hack a bit
#                     ssid = self._split_sid(sid)
#                     uid =None
#                     ddisk = ""
#                     for k,v in pnps.items():
#                         if ssid in v:
#                             uid = self._make_uid(vid,pid,k)
#                             ddisk = self._get_drive_letter_from_id(k)
#                             break
#                 if uid:
#                     dev = {
#                         "uid":uid,
#                         "vendor":vid,
#                         "model":pid,
#                         "serial":sid,
#                         "port":x.DeviceID,
#                         "devstring":x.Description,
#                         "disk":ddisk
#                     }
#                     dfnd.add(uid)
#                     self.cdevs[uid]=dev
#                     serdev.append(uid)
#         usbdevs = self._get_hw(pnps.keys(),serdev)
#         #print("SERDEV",serdev)
#         matchcom = re.compile(".*\((COM[0-9]+)\).*")
#         for iid,usbdev in usbdevs.items():
#             #print(iid,"==>",usbdev.PNPDeviceID)
#             vid,pid,sid,uid = self._get_win_device_id(usbdev.PNPDeviceID)
#             if uid:
#                 dev = {
#                     "uid":uid,
#                     "vendor":vid,
#                     "model":pid,
#                     "serial":sid,
#                     "port":"NULL",
#                     "devstring":usbdev.Name,
#                     "disk":""
#                 }
#                 mth = matchcom.match(usbdev.Name)
#                 if mth:
#                     dev["port"]=mth.group(1)
#                 dfnd.add(uid)
#                 self.cdevs[uid]=dev
#         #print(self.cdevs)
#         ddnd = set()
#         for k in self.devices:
#             ddnd.add(k)
#         if dfnd>=ddnd and dfnd<=ddnd:
#             return
#         self.b_lock.acquire()
#         self.devices = self.cdevs
#         self.fresh_boards=True
#         self.b_lock.release()

# ######################################## MAC
#     def setup_mac(self):
#         self.macusb = macusb.MacUsb()
#     def stop_mac(self):
#         pass
#     def check_dev_mac(self,dev,action="add"):
#         pass
#     def _get_mount_point_mac(self,disk):
#         try:
#             out = subprocess.check_output("diskutil info "+disk,universal_newlines=True,shell=True)
#             lines = out.split("\n")
#             for line in lines:
#                 if "Mount Point:" in line:
#                     return line.replace("Mount Point:","").strip()
#             return disk
#         except:
#             return disk
#     def ioreg(self):
#         try:
#             return subprocess.check_output("ioreg -x -r -l -c "+self.iousbstring,universal_newlines=True,shell=True)
#         except:
#             return ""
#     def parse(self):
#         nodes = self.macusb.get_nodes()
#         devs = set()
#         nodes_ok = set()
#         props = {
#             "idVendor":"vendor",
#             "idProduct":"model",
#             "USB Serial Number":"serial",
#             "USB Product Name":"serial_id",
#             "IODialinDevice":"port",
#             "BSD Name":"disk"
#         }
#         devices = []
#         for iid,node in nodes.items():
#             if node.id in nodes_ok:
#                 #print(node.name,"excluded")
#                 continue
#             nodes_ok.add(node.id)
#             vendor = node.has_vendor()
#             if vendor and vendor in self.vendors and node.cls==self.macusb.iousbstring:
#                 dev = {"devstring":node.name}
#                 candidates = [node]+[nodes[x] for x in node.descendants]
#                 for k,v in props.items():
#                     for dnode in candidates:
#                         if k in dnode.properties():
#                             dev[v]=dnode.get_property(k).strip('"')
#                             if v=="disk":
#                                 dev[v]=self._get_mount_point_mac(dev[v])
#                             break
#                 nodes_ok.update(node.descendants)
#                 dev["uid"]=self._make_uid(dev["vendor"],dev["model"],dev["serial"])
#                 devices.append(dev)
#         devlist = {}
#         for dev in devices:
#             devlist[dev["uid"]]=dev
#         return devlist

#         # dev = {}
#         # for k,node in nodes.items():

#         #     if line.startswith("+"):
#         #         #got a device
#         #         if dev:
#         #             devices.append(dev)
#         #         dev = {"devstring":line[:line.find("<")]}
#         #     elif "idVendor" in line:
#         #         dev["vendor"]=line[line.find("0x")+2:].upper()
#         #     elif "idProduct" in line:
#         #         dev["model"]=line[line.find("0x")+2:].upper()
#         #     elif "USB Serial Number" in line:
#         #         dev["serial"]=line[line.find("= \"")+3:-1].upper()
#         #     elif "USB Product Name" in line:
#         #         dev["serial_id"]=line[line.find("= \"")+3:-1]
#         #     elif "IODialinDevice" in line:
#         #         dev["port"]=line[line.find("= \"")+3:-1]
#         #     elif "BSD Name" in line:
#         #         dev["disk"]=line[line.find("= \"")+3:-1]
#         #         dev["disk"]=self._get_mount_point_mac(dev["disk"])
#         # if dev and dev not in devices:
#         #     devices.append(dev)

#         # devlist = {}
#         # for dev in devices:
#         #     if "model" in dev and "vendor" in dev and "serial" in dev:
#         #         vendor = dev["vendor"].strip()
#         #         model = dev["model"].strip()
#         #         if len(vendor)<4:
#         #             vendor=("0"*(4-len(vendor)))+vendor
#         #         if len(model)<4:
#         #             model=("0"*(4-len(model)))+model
#         #         dev["uid"]=self._make_uid(vendor,model,dev["serial"])
#         #         devlist[dev["uid"]]=dev
#         #         dev["vendor"]=vendor
#         #         dev["model"]=model
#         # return devlist

#     def run_mac(self):
#         time.sleep(1)
#         devs = self.parse()
#         #print(devs)
#         deepequal = True
#         if devs.keys()==self.devices.keys():
#             for k,v in devs.items():
#                 if v.keys()!=self.devices[k].keys():
#                     deepequal=False
#                     break
#         else:
#             deepequal=False
#         if not deepequal:
#             self.b_lock.acquire()
#             self.devices = devs
#             self.fresh_boards=True
#             self.b_lock.release()
