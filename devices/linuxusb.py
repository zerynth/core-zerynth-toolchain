import pyudev
from base import *
		
class LinuxUsb():

	def __init__(self):
		self.devstrings={
				"ID_SERIAL":"serial",
				"ID_SERIAL_SHORT":"sid",
				"ID_VENDOR_ID":"vid",
				"ID_MODEL_ID":"pid",
				"SUBSYSTEM":"sys",
				"DEVNAME":"dev"
			}
		self.devkeys = set(self.devstrings.keys())
		self.udev = pyudev.Context()
	
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

	def parse(self):
		devices = []
		try:
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
							devices.append(dev)
					elif "SUBSYSTEM" in device and device["SUBSYSTEM"] in ("hid"):
						dev = {
							"vid":device["HID_ID"].split(":")[0][-4:],
							"pid":device["HID_ID"].split(":")[1][-4:],
							"sid":device["HID_ID"],
							"port": None,
							"block": None,
							"disk": None,
							"desc":device["HID_NAME"]
						}
						devices.append(dev)
				except Exception as e:
					warning("Exception in usb discover: ",str(e))
		except Exception as e:
			warning("Exception in usb discover: ",str(e))
		return devices
				