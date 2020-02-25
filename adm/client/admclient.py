from base.zrequests import TimeoutException
from base.zrequests import zget, zpost, zput

from .errors import NotFoundError
from .models import Device
from .models import DeviceKey
from .models import Fleet
from .models import Workspace
from .logging import MyLogger

logger = MyLogger().get_logger()


class ADMClient(object):
    """
    A client for communicating with the API of ADM.
    Example:
        >>> import adm
        >>> client = adm.ADMClient(rpc_url="http://127.0.0.1:8000")

    """

    def __init__(self, rpc_url="http://127.0.0.1:7777", workspace_url="http://127.0.0.1:8001",
                 device_url="http://127.0.0.1:8001", fleet_url="http://api.localhost/v1/device/"):
        self.rpc_url = rpc_url
        self.workspace_url = workspace_url
        self.device_url = device_url
        self.fleet_url = fleet_url

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
            return Workspace.from_json(data['workspace'])
        else:
            logger.error("Error in getting the workspace {}".format(res.text))
            raise NotFoundError(res.text)

    def workspace_get(self, workspace_id):
        path = "{}{}/".format(self.workspace_url, workspace_id)
        logger.info("Get the {} workspace: {}".format(workspace_id, path))
        r = zget(path)
        if r.status_code == 200:
            data = r.json()
            return Workspace.from_json(data)
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
        # curl -d '{"name":"prova"}' POST http://api.zerinth.com/v1/device/dev-4m2vxgc5k935/key
        # key = POST http://api.zerinth.com/v1/device/dev-4m2vxgc5k935/key {"name":"prova"}
        # key.id
        # key.raw
        # exp =  '09/19/18 13:55:26'
        # jwt = device.encode_jwt(auth_keyid=key.id, secret=key.raw, exp=DEVICE_AUTHKEY_EXPIRATION)))
        # jwt is the password for the device
        path = "{}{}/key".format(self.device_url, devid)
        payload = {"Name": name}
        res = zpost(path, data=payload)
        if res.status_code == 200:
            data = res.json()
            return DeviceKey.from_json(data["key"])
        else:
            logger.error("Error in getting the workspace of a device {}".format(res.text))
            raise NotFoundError(res.text)

    def device_get_workspace(self, devid):
        path = "{}{}/workspace".format(self.device_url, devid)
        logger.info("Get the workspace of a device")
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
