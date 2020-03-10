import base64
from datetime import datetime
from datetime import timedelta

from base.jwt.api_jwt import encode


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
