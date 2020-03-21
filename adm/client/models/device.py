from .base import Model, Collection


class DeviceModel(Model):

    @property
    def fleet_id(self):
        return self.attrs.get("fleet_id")

    @property
    def workspace_id(self):
        res = self.client.api.workspace_of_device(self.id)
        return res.get(self.id_attribute)

    def create_key(self, name):
        key = self.client.api.devices.create_device_key(self.id, name)


class DeviceCollection(Collection):
    model = DeviceModel

    def list(self):
        """
        List devices
        """
        resp = self.client.api.devices()
        return [self.prepare_model(r) for r in resp]

    def create(self, name, description=""):
        """
        Create a device

        Args:
            name (str): name of the device.
            fleet_id (str): fleet id where the device is associated.

        Returns:
            A :py:class:`Device` object.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.create_device(name, description)
        return self.prepare_model(resp)

    def get(self, device_id):
        """
        Get a device by ID.

        Args:
            device_id (str): Device ID.

        Returns:
            A :py:class:`Device` object.

        Raises:
            :py:class:`adm.errors.NotFound`
                If the device does not exist.
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.get_device(device_id)
        return self.prepare_model(resp)

    def update(self, device_id, name, fleet_id=None):
        """
        Update a device.

        Args:
            device_id (str): Device ID.
            name (str): the new name of the device
            fleet_id (str): the fleet id to be assigned [Default: None]

        Returns:
            A :py:class:`Device` object.

        Raises:
            :py:class:`adm.errors.NotFound`
                If the device does not exist.
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.update_device(device_id, name, fleet_id)
        return resp


class Device:
    """Device class represent a device"""

    def __init__(self, id, name, fleet_id=None):
        self.id = id
        self.name = name
        self.fleet_id = fleet_id
        self.keys = []

    @staticmethod
    def from_json(dev):
        # {"Device":{"id":"dev-4lvyidx953wh","name":"dica","fleet_id":"","created_at":"2020-01-21T15:41:35.837857Z"}}
        # dev = json["device"]
        return Device(dev["id"], dev["name"], dev["fleet_id"] if dev["fleet_id"] is not "" else None)

    def __str__(self):
        return "Device: id: {}, name:{}, fleetId :{}".format(self.id, self.name, self.fleet_id)

    @property
    def Id(self):
        return self.id

    @property
    def Name(self):
        return self.name

    @property
    def FleetID(self):
        return self.fleet_id

    def add_key(self, device_key):
        self.keys.append(device_key)
