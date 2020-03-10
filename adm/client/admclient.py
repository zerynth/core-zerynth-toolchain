import base64

from base.zrequests import TimeoutException
from base.zrequests import zget, zpost, zput

from .errors import NotFoundError
from .logging import MyLogger
from .models import Device
from .models import DeviceKey
from .models import Firmware
from .models import Fleet
from .models import Status
from .models import Workspace

logger = MyLogger().get_logger()


class ADMClient(object):
    """
    A client for communicating with the API of ADM.
    Example:
        >>> import adm
        >>> client = adm.ADMClient(rpc_url="http://127.0.0.1:8000")

    """

    def __init__(self, rpc_url="http://127.0.0.1:7777", workspace_url="http://127.0.0.1:8001",
                 device_url="http://127.0.0.1:8001", fleet_url="http://api.localhost/v1/device/",
                 status_url="http://api.localhost/v1/status"):
        self.rpc_url = rpc_url
        self.workspace_url = workspace_url
        self.device_url = device_url
        self.fleet_url = fleet_url
        self.status_url = status_url

    def workspace_all(self):
        try:
            res = zget(self.workspace_url)
            if res.status_code == 200:
                data = res.json()
                workspaces = [Workspace.from_json(w) for w in data["workspaces"]]
                return workspaces
            else:
                print("Error in getting the workspace {}".format(res.text))
                raise NotFoundError(res.text)
        except TimeoutException as e:
            print("No answer yet")
        except Exception as e:
            print("Can't get workspaces: err s{}".format(e))

    def workspace_create(self, name):
        data = {"name": name}
        res = zpost(self.workspace_url, data=data)
        if res.status_code == 200:
            data = res.json()
            print(data)
            return Workspace.from_json(data['workspace'])
        else:
            logger.error("Error in getting the workspace {}".format(res.text))
            raise NotFoundError(res.text)

    def workspace_get(self, workspace_id):
        path = "{}{}".format(self.workspace_url, workspace_id)
        logger.info("Get the {} workspace: {}".format(workspace_id, path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Workspace.from_json(data["workspace"])
        else:
            logger.error("Error in getting the workspace {}".format(r.text))
            raise NotFoundError(r.text)

    def device_create(self, name, fleetId=None):
        payload = {
            "name": name,
            "fleet_id": None if fleetId is None else fleetId
        }
        logger.debug("Creating device {}: {}".format(name, self.device_url))
        r = zpost(self.device_url, data=payload)
        if r.status_code == 200:
            data = r.json()
            return Device.from_json(data['device'])
        else:
            logger.info(r.text)
            logger.error("Error creating the device")
            raise NotFoundError(r.text)

    def device_get(self, id):
        path = "{}{}/".format(self.device_url, id)
        logger.info("Getting the device {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Device.from_json(data["device"])
        else:
            logger.info(r.text)
            logger.error("Error in getting the device {}")
            raise NotFoundError(r.text)

    def device_update(self, device_id, name, fleet_id):
        path = "{}{}/".format(self.device_url, device_id)
        logger.info("Updating device {}: path {}".format(device_id, path))
        payload = {"Name": name, "fleet_id": fleet_id}
        try:
            res = zput(path, data=payload)
            if res.status_code == 200:
                return "ok"
            else:
                print("Error in getting all devices {}".format(res.text))
                raise NotFoundError(res.text)
        except TimeoutException as e:
            print("No answer yet")
        except Exception as e:
            print("Can't get devices: err s{}".format(e))

    #
    def device_all(self):
        try:
            res = zget(self.device_url)
            if res.status_code == 200:
                data = res.json()
                devices = [Device.from_json(w) for w in data["devices"]]
                return devices
            else:
                print("Error in getting all devices {}".format(res.text))
                raise NotFoundError(res.text)
        except TimeoutException as e:
            print("No answer yet")
        except Exception as e:
            print("Can't get devices: err s{}".format(e))

    def device_create_key(self, name, devid):
        path = "{}{}/key".format(self.device_url, devid)
        payload = {"Name": name}
        res = zpost(path, data=payload)
        if res.status_code == 200:
            data = res.json()
            return DeviceKey.from_json(data["key"])
        else:
            logger.error("Error in getting the workspace of a device {}".format(res.text))
            raise NotFoundError(res.text)

    def device_all_key(self, devid):
        path = "{}{}/key".format(self.device_url, devid)
        res = zget(path)
        if res.status_code == 200:
            data = res.json()
            return [DeviceKey.from_json(key) for key in data["keys"]]
        else:
            logger.error("Error in getting the workspace of a device {}".format(res.text))
            raise NotFoundError(res.text)

    def device_get_workspace(self, devid):
        path = "{}{}/workspace".format(self.device_url, devid)
        logger.info("Geting the workspace of a device")
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Workspace.from_json(data["workspace"])
        else:
            logger.error("Error in getting the workspace of a device {}".format(r.text))
            raise NotFoundError(r.text)

    def fleet_create(self, name, workspace_id):
        payload = {"Name": name, "workspace_id": workspace_id}
        logger.debug("Path create fleet: {}".format(self.fleet_url))
        logger.info("Creating fleet: {}".format(name))
        r = zpost(self.fleet_url, data=payload)
        if r.status_code == 200:
            data = r.json()
            return Fleet.from_json(data["fleet"])
        else:
            logger.error("Error in getting the workspace {}".format(r.text))
            raise NotFoundError(r.text)

    def fleet_all(self):
        try:
            res = zget(self.fleet_url)
            if res.status_code == 200:
                data = res.json()
                fleets = [Fleet.from_json(w) for w in data["fleets"]]
                return fleets
            else:
                print("Error in getting all fleets {}".format(res.text))
                raise NotFoundError(res.text)
        except TimeoutException as e:
            print("No answer yet")
        except Exception as e:
            print("Can't get fleets: err s{}".format(e))

    def fleet_get(self, id):
        path = "{}{}".format(self.fleet_url, id)
        logger.info("Getting the fleet {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Fleet.from_json(data["fleet"])
        else:
            logger.info(r.text)
            logger.error("Error in getting the device {}")
            raise NotFoundError(r.text)

    ##############################
    #   Change set
    ##############################

    def _create_changeset(self, key, value, targets):
        path = "{}changeset".format(self.status_url)
        logger.debug("Creating a changeset: {}".format(path))
        payload = {"key": key, "value": value, "targets": targets}
        logger.debug(payload)
        r = zpost(path, data=payload)
        if r.status_code == 200:
            data = r.json()
            return data["id"]
        else:
            logger.error("Error in creating the changeset {}, {}".format(r.status_code, r.text))
            raise NotFoundError(r.text)

    def _get_current_device_status(self, device_id):
        # /status/currentstatus/{devid}
        path = "{}currentstatus/{}".format(self.status_url, device_id)
        logger.info("Get the current status of {} device: {}".format(device_id, path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            datastatus = data['status'] if "status" in data and data["status"] and not None else {}
            status = []
            for key, value in datastatus.items():
                s = Status(key, value['v'], value['t'])
                status.append(s)
            return status
        else:
            logger.error("Error in creating the changeset {}, {}".format(r.status_code, r.text))
            raise NotFoundError(r.text)

    def _get_expected_status(self, device_id):
        path = "{}expected/{}".format(self.status_url, device_id)
        logger.info("Get the expected status of {} device: {}".format(device_id, path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            datastatus = data['status'] if "status" in data and data["status"] and not None else {}
            status = []
            for key, value in datastatus.items():
                s = Status(key, value['v'], value['t'])
                status.append(s)
            return status
        else:
            logger.error("Error in creating the changeset {}, {}".format(r.status_code, r.text))
            raise NotFoundError(r.text)

    ##################################
    # Firmware
    ################################

    def get_firmware_metadata(self, worksapce_id, firmware_id):
        path = "{}/{}/firmware/{}".format(self.status_url, worksapce_id, firmware_id)
        logger.info("Getting a firmware metadata: {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Fleet.from_json(data["fleet"])
        else:
            logger.info(r.text)
            logger.error("Error in getting the device {}")
            raise NotFoundError(r.text)

    def firmware_upload(self, workspace_id, files_path, version, metadata):
        path = "{}{}/firmware/{}".format(self.workspace_url, workspace_id, version)
        binsbase64 = []
        for filename in files_path:
            print("reading sfile", filename)
            with open(filename, "rb") as image_file:
                enc64 = base64.b64encode(image_file.read())
                binsbase64.append(enc64.decode("utf8"))
        payload = {"bin": binsbase64, "metadata": metadata, "description": ""}
        r = zpost(path, payload)
        if r.status_code == 200:
            data = r.json()
            return Firmware.from_json(data["firmware"])
        else:
            logger.info(r.text)
            logger.error("Error in uploading the firmware {}")
            raise NotFoundError(r.text)

    def firmware_all(self, workspace_id):
        path = "{}{}/firmware".format(self.workspace_url, workspace_id)
        logger.info(path)
        try:
            res = zget(path)
            if res.status_code == 200:
                data = res.json()
                firm = [Firmware.from_json(w) for w in data["firmwares"]]
                return firm
            else:
                print("Error in getting all fleets {}".format(res.text))
                raise NotFoundError(res.text)
        except TimeoutException as e:
            print("No answer yet")
        except Exception as e:
            print("Can't get firmwwares. {}".format(e))

    def fota_schedule(self, fw_version, devices, on_time=""):
        value = {"fw_version": fw_version, "on_schedule": on_time}
        return self._create_changeset("@fota", value, devices)

    def fota_check(self, devices):
        map_fota = []
        for dev in devices:
            current_status = [status for status in self._get_current_device_status(dev) if status.is_fota()]
            expected_status = [status for status in self._get_expected_status(dev) if status.is_fota()]
            status_msg = "<none>"
            if len(expected_status) > 0 and len(current_status) == 0:
                status_msg = "Scheduled"
            elif len(current_status) > 0:
                status = current_status[0]
                status_msg = status.value
            d = {"device": dev, "status": status_msg}
            map_fota.append(d)
        return map_fota
