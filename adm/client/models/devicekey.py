import base64
from datetime import datetime
from datetime import timedelta

from base.jwt.api_jwt import encode

from .base import Model, Collection


class DeviceKeyModel(Model):

    @property
    def created_at(self):
        return self.attrs.get("created_at")

    @property
    def device_id(self):
        return self.attrs.get("device_id")

    @property
    def raw(self):
        return self.attrs.get("raw")

    @property
    def expire_at(self, days=31):
        # default expiraton time is 1 month
        exp = self._create_exp_time(days)
        return exp.strftime('%B %d %Y - %H:%M:%S')

    @property
    def is_revoked(self):
        return self.attrs.get("revoked")

    def _create_exp_time(self, delta_days=31):
        return datetime.utcnow() + timedelta(days=delta_days)

    def as_jwt(self, exp_delta_in_days=31):
        exp = self._create_exp_time(exp_delta_in_days)
        key = base64.b64decode(self.raw)
        encoded_jwt = encode({'sub': self.device_id, "user": self.device_id, "key": self.id, "exp": exp}, key,
                             algorithm='HS256')
        return encoded_jwt.decode("utf-8")


class DeviceKeyCollection(Collection):
    model = DeviceKeyModel

    def create(self, device_id, name):
        """
        Create a new authentication key for a device

        Args:
            device_id (str): the Device Id.
            name (str): name of the key.
        Returns:
            A :py:class:`DeviceKey` object.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.create_device_key(device_id, name)
        return self.prepare_model(resp)

    def list(self, device_id):
        """
        List the key of a device.

        Args:
            device_id (str): The Device Id.

        Returns:
            A :py:class:`DeviceKey` list.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        keys = self.client.api.list_device_keys(device_id)
        return [self.prepare_model(k) for k in keys]

    def get(self, device_id, key_id):
        """
        Get a device key by id.

        Args:
            device_id (str): The Device Id.
            key_id (str): The key id..

        Returns:
            A :py:class:`DeviceKey` list.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        key = self.client.api.get_device_key(device_id, key_id)
        return self.prepare_model(key)

class DeviceKey:
    """DeviceKey is the symmetric key of a device"""

    def __init__(self, id, devid, name, raw_key, revoked):
        self.id = id
        self.device_id = devid
        self.name = name
        self.raw_key = raw_key
        self.revoked = revoked

        # default expiraton time is 1 month
        self.exp = self.set_exp_time(31)

    @staticmethod
    def from_json(device_key):
        # "key": {
        #     "id": 1,
        #     "name": "testadsf",
        #     "raw": "sdHmLrL1Bj4u0jAuUbeX4BhH+g0ANa1x6/ROFNNDuU8=",
        #     "type": "SYM256",
        #     "revoked": false,
        #     "device_id": "dev-4pbq2056woz2",
        #     "created_at": "0001-01-01T00:00:00Z",
        #     "account_id": "OsbDq5jtSwmmPi5I5bNyYw"
        # }
        return DeviceKey(device_key["id"], device_key["device_id"], device_key["name"], device_key["raw"],
                         device_key["revoked"])

    def __str__(self):
        return "Key: id: {}, name:{}, revoked :{}".format(self.id, self.name, self.revoked)

    def set_exp_time(self, delta_days=31):
        return datetime.utcnow() + timedelta(days=delta_days)

    def as_jwt(self, exp_delta_in_days=None):
        if exp_delta_in_days is not None:
            self.exp = self.set_exp_time(exp_delta_in_days)

        key = base64.b64decode(self.raw)
        encoded_jwt = encode({'sub': self.device_id, "user": self.device_id, "key": self.id, "exp": self.exp}, key,
                             algorithm='HS256')
        return encoded_jwt.decode("utf-8")

    @property
    def Expiration(self):
        return self.exp.strftime('%B %d %Y - %H:%M:%S')

    @property
    def Id(self):
        return self.id

    @property
    def raw(self):
        return self.raw_key

    @property
    def Name(self):
        return self.name
