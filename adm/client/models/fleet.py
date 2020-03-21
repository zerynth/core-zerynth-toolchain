from .device import Device
from .base import Model, Collection


class FleetModel(Model):

    @property
    def devices(self):
        devices = []
        if self.attrs.get("devices"):
            for d in self.attrs.get("devices"):
                devices.append(d[self.id_attribute])
        return devices

    @property
    def workspace_id(self):
        return self.attrs.get("workspace_id")


class FleetCollection(Collection):
    model = FleetModel

    def list(self):
        """
        List fleets
        """
        resp = self.client.api.fleets()
        return [self.prepare_model(r) for r in resp]

    def create(self, name, description=""):
        """
        Create a fleet

        Args:
            name (str): name of the device.
            fleet_id (str): fleet id where the device is associated.

        Returns:
            A :py:class:`Device` object.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.create_fleet(name, description)
        return self.prepare_model(resp)

    def get(self, device_id):
        """
        Get a device by ID.

        Args:
            device_id (str): device ID.

        Returns:
            A :py:class:`device` object.

        Raises:
            :py:class:`adm.errors.NotFound`
                If the device does not exist.
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.get_fleet(device_id)
        return self.prepare_model(resp)

class Fleet:
    """Fleet class represent a fleet"""

    def __init__(self, id, name, workspace_id, devices=[]):
        self.id = id
        self.name = name
        self.workspace_id = workspace_id
        self.devices = []

    @staticmethod
    def from_json(fleet):
        # {"fleet":{"id":"flt-4lvzygd9n6yp","name":"dsfòlk","description":"","workspace_id":"",
        # "devices":null,"created_at":"2020-01-21T15:57:48.647735Z"}}
        # fleet = json["fleet"]
        devices = []
        print(fleet)
        if fleet["devices"] is not None:
             devices = [Device.from_json(d) for d in fleet["devices"]]
        return Fleet(fleet["id"], fleet["name"], fleet["workspace_id"] if fleet["workspace_id"] is not "" else None,
                     devices)

    def __str__(self):
        return "Fleet: id: {}, name:{}, workspace_id :{}, devices: {}".format(self.id, self.name, self.workspace_id,
                                                                              self.devices)

    @property
    def Name(self):
        return self.name

    @property
    def Id(self):
        return self.id

    @property
    def Devices(self):
        return self.devices

    @property
    def WorkspaceId(self):
        return self.workspace_id
