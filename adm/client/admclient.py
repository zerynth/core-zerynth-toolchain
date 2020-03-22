from base.zrequests import zget, zpost, zput, zdelete

from .errors import NotFoundError
from .logging import MyLogger
from .models import Gate

logger = MyLogger().get_logger()


class ADMClient(object):
    """
    A client for communicating with the API of ADM.
    Example:
        >>> import adm
        >>> client = adm.ADMClient()

    """

    def __init__(self, status_url="http://api.localhost/v1/status",
                 gates_url="http://api.localhost/v1/gate",
                 ):
        self.status_url = status_url
        self.gate_url = gates_url

    ##################################
    # Fota
    ################################s

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
                       "X-Auth-Token": token
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
