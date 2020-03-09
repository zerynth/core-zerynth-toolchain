from base import jwt
from datetime import datetime
from datetime import timedelta

class DeviceKey:
    """DeviceKey is the symmetric key of a device"""

    def __init__(self, id, devid, name, raw_key, revoked):
        self.id = id
        self.device_id = devid
        self.name = name
        self.raw_key = raw_key
        self.revoked = revoked

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
        print("keys", device_key)
        return DeviceKey(device_key["id"], device_key["device_id"], device_key["name"], device_key["raw"],
                         device_key["revoked"])

    def __str__(self):
        return "Key: id: {}, name:{}, revoked :{}".format(self.id, self.name, self.revoked)

    @property
    def as_jwt(self):
        exp = datetime.utcnow() + timedelta(days=31)
        print("endocidifn")
        data = jwt.encode({'sub': self.device_id, 'user': self.device_id, 'exp': 1, 'key': self.Id}, self.raw, algorithm='HS256')
        base64.b64decode("f1JPEcc3Bmn3PWqsMSAsr74IwjeKyGWUNiLCO2ot0Ww=")
        jwt.encode({'sub': "dev-4pc2ycnlob9h", 'user': "dev-4pc2ycnlob9h", 'exp': 1, 'key':1},"f1JPEcc3Bmn3PWqsMSAsr74IwjeKyGWUNiLCO2ot0Ww=", algorithm='HS256')
        return data.decode("utf-8")
        # key.id
        # key.raw
        # exp =  '09/19/18 13:55:26'
        # jwt = device.encode_jwt(auth_keyid=key.id, secret=key.raw, exp=DEVICE_AUTHKEY_EXPIRATION)))

    @property
    def Id(self):
        return self.id

    @property
    def raw(self):
        return self.raw_key
