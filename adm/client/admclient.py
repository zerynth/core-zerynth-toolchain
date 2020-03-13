import base64

from base.zrequests import TimeoutException
from base.zrequests import zget, zpost, zput, zdelete

from .errors import NotFoundError
from .logging import MyLogger
from .models import DataTag
from .models import Device
from .models import DeviceKey
from .models import Firmware
from .models import Fleet
from .models import Status
from .models import Workspace
from .models import Gate
logger = MyLogger().get_logger()


class ADMClient(object):
    """
    A client for communicating with the API of ADM.
    Example:
        >>> import adm
        >>> client = adm.ADMClient(rpc_url="http://127.0.0.1:8000")

    """

    def __init__(self, rpc_url="http://127.0.0.1:7777",
                 workspace_url="http://127.0.0.1:8001",
                 device_url="http://127.0.0.1:8001",
                 fleet_url="http://api.localhost/v1/device/",
                 status_url="http://api.localhost/v1/status",
                 gates_url="http://api.localhost/v1/gate",
                 data_url="http://api.localhost/v1/tsmanager/",
                 ):
        self.rpc_url = rpc_url
        self.workspace_url = workspace_url
        self.device_url = device_url
        self.fleet_url = fleet_url
        self.status_url = status_url
        self.gate_url = gates_url
        self.data_url = data_url

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

    def workspace_create(self, name, description=""):
        data = {"name": name, "description": description}
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
        logger.debug("Get the {} workspace: {}".format(workspace_id, path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Workspace.from_json(data["workspace"])
        else:
            logger.error("Error in getting the workspace {}".format(r.text))
            raise NotFoundError(r.text)

    def workspace_tags_all(self, workspace_id):
        path = "{}workspace/{}/tags".format(self.data_url, workspace_id)
        logger.debug("Get the tags of the workspace {}, {}".format(workspace_id, path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            if "tags" in data:
                return [tag for tag in data["tags"]]
            else:
                []
            # return Workspace.from_json(data["workspace"])
        else:
            logger.error("Error in getting tags of a workspace {}".format(r.text))
            raise NotFoundError(r.text)

    def workspace_get_devices(self, workspace_id):
        path = self.urljoin(self.workspace_url, workspace_id, "devices")
        logger.debug("Get the tags of the workspace {}, {}".format(workspace_id, path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            if "devices" in data and data["devices"] is not None:
                return [Device.from_json(device) for device in data["devices"]]
            else:
                return []
        else:
            logger.error("Error in getting devices of a workspace {}".format(r.text))
            raise NotFoundError(r.text)

    def workspace_data_get(self, workspace_id, tag, device_id=None):
        # todo filter by devices the tags
        path = "{}workspace/{}/tag/{}".format(self.data_url, workspace_id, tag)
        logger.debug("Getting tags of a workspace {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            res = data["result"]
            return [DataTag.from_json(data) for data in res]
        else:
            logger.debug(r.text)
            logger.error("Error in getting the device {}")
            raise NotFoundError(r.text)

    ##############################
    #   Device
    ##############################

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
            logger.debug(r.text)
            logger.error("Error creating the device")
            raise NotFoundError(r.text)

    def device_get(self, id):
        path = "{}{}/".format(self.device_url, id)
        logger.debug("Getting the device {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Device.from_json(data["device"])
        else:
            logger.debug(r.text)
            logger.error("Error in getting the device {}")
            raise NotFoundError(r.text)

    def device_update(self, device_id, name, fleet_id):
        path = "{}{}/".format(self.device_url, device_id)
        logger.debug("Updating device {}: path {}".format(device_id, path))
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

    def device_all(self):
        try:
            res = zget(self.device_url)
            if res.status_code == 200:
                data = res.json()
                if "devices" in data and data["devices"] is not None:
                    return [Device.from_json(w) for w in data["devices"]]
                else:
                    return []
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
        logger.debug("Getting the workspace of a device")
        logger.debug("Getting the workspace of a device")
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Workspace.from_json(data["workspace"])
        else:
            logger.error("Error in getting the workspace of a device {}".format(r.text))
            raise NotFoundError(r.text)

    ##############################
    #   Fleet
    ##############################
    def fleet_create(self, name, workspace_id):
        payload = {"Name": name, "workspace_id": workspace_id}
        logger.debug("Path create fleet: {}".format(self.fleet_url))
        logger.debug("Creating fleet: {}".format(name))
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
        logger.debug("Getting the fleet {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Fleet.from_json(data["fleet"])
        else:
            logger.debug(r.text)
            logger.error("Error in getting the device {}")
            raise NotFoundError(r.text)

    ##############################
    #   Change set
    ##############################

    def _create_changeset(self, key, value, targets):
        path = "{}changeset".format(self.status_url)
        logger.debug("Creating a changeset: {}".format(path))
        payload = {"key": key, "value": value, "targets": targets}
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
        logger.debug("Get the current status of {} device: {}".format(device_id, path))
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

    def _get_expected_device_status(self, device_id):
        path = "{}expected/{}".format(self.status_url, device_id)
        logger.debug("Get the expected status of {} device: {}".format(device_id, path))
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
        logger.debug("Getting a firmware metadata: {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Fleet.from_json(data["fleet"])
        else:
            logger.debug(r.text)
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
            logger.debug(r.text)
            logger.error("Error in uploading the firmware {}")
            raise NotFoundError(r.text)

    def firmware_all(self, workspace_id):
        path = "{}{}/firmware".format(self.workspace_url, workspace_id)
        logger.debug(path)
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
            expected_status = [status for status in self._get_expected_device_status(dev) if status.is_fota()]
            status_msg = "<none>"
            if len(expected_status) > 0 and len(current_status) == 0:
                status_msg = "Scheduled"
            elif len(current_status) > 0:
                status = current_status[0]
                status_msg = status.value
            d = {"device": dev, "status": status_msg}
            map_fota.append(d)
        return map_fota

    ##############################
    #   Gate: WebHook
    ##############################
    def gate_workspace_all(self, workspace_id, status, origin):
        path = self.urljoin(self.gate_url, "workspace", workspace_id)
        params = {"status": status, "origin": origin}
        r = zget(path, params=params)
        if r.status_code == 200:
            data = r.json()
            if "gates" in data and data["gates"] is not None:
                return [Gate.from_json(gate) for gate in data["gates"]]
            return []
        else:
            logger.debug(r.text)
            logger.error("Error in getting all the tags for workspace {}", workspace_id)
            raise NotFoundError(r.text)

    def gate_webhook_data_create(self, name, url, token, period, workspace_id, tag):
        path = "{}/webhook/".format(self.gate_url)
        logger.info("Creating a webhook: {}".format(path))
        payload = {"name": name, "url": url, "content-type": "application/json", "period": period,
                   "origin": "data",
                   "payload": {"tag": tag, "workspace_id": workspace_id},
                   "tokens": {
                       "X-Auth-Token":token
                   }}
        logger.info(payload)
        r = zpost(path, data=payload)
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            logger.error("Error in creating the webhook {}, {}".format(r.status_code, r.text))
            raise NotFoundError(r.text)

    def gate_get(self, gate_id):
        path = self.urljoin(self.gate_url, gate_id)
        logger.debug("Getting the Gate: {}".format(path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            if "gate" in data and data["gate"] is not None:
                return Gate.from_json(data["gate"])
            return None
        else:
            logger.error("Error in creating the webhook {}, {}".format(r.status_code, r.text))
            raise NotFoundError(r.text)

    def gate_update(self, gate_id, name=None, status=None, period=None, url=None):
        path = self.urljoin(self.gate_url, gate_id)
        payload = {}
        if name:
            payload["name"] = name
        if status:
            payload["status"] = status
        if period:
            payload["period"] = period
        if url:
            payload["url"] = url
        try:
            res = zput(path, data=payload)
            if res.status_code == 200:
                return "Gate Updated succesfully"
            else:
                return None
        except Exception as e:
            print(e)

    def gate_delete(self, gate_id):
        path = self.urljoin(self.gate_url, gate_id)
        logger.debug("Deleting gate : {}".format(path))
        try:
            res = zdelete(path)
            if res.status_code == 200:
                return "Gate deleted succesfully"
            else:
                return None
        except Exception as e:
            print(e)

    ##############################
    #   Job
    ##############################

    def job_schedule(self, name, args, devices, on_time=""):

        value = {"args”": { }, "on_schedule": on_time}

        if not name.startswith('@'):
            name = "@" + name
        return self._create_changeset(name, value, devices)

    def urljoin(self, base_path, *args):
        """
        Joins given arguments into an url. Trailing but not leading slashes are
        stripped for each argument.

        Example
           urljoin("hello",  "world"))   ->  hello/world
           urljoin("/hello",  "world")   -> /hello/world
           urljoin("hello/",  "world")   -> hello/world
           urljoin("hello/",  "world/")   -> hello/world
           urljoin("hello/",  "/world/")  ->  hello//world
        """

        # return "/".join(map(lambda x: str(x).rstrip('/'), args))
        return base_path + "/".join(map(lambda x: str(x).rstrip('/'), args))