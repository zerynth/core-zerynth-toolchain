import base64

from base.zrequests import TimeoutException
from base.zrequests import zget, zpost, zput, zdelete

from .errors import NotFoundError
from .logging import MyLogger
from .models import DeviceKey
from .models import Firmware
from .models import Fleet
from .models import Status
from .models import Gate
from .helper import convert_into_job

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
                 status_url="http://api.localhost/v1/status",
                 gates_url="http://api.localhost/v1/gate",
                 ):
        self.rpc_url = rpc_url
        self.workspace_url = workspace_url
        self.device_url = device_url
        self.status_url = status_url
        self.gate_url = gates_url


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
        value = {"args": args, "on_schedule": on_time}
        name = convert_into_job(name)
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