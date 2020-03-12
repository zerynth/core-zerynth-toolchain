import base64
from datetime import datetime
from datetime import timedelta

from base.jwt.api_jwt import encode


class DataTag:
    """DataTag is a single data sent by the device to a tag"""

    def __init__(self, tag, timestamp, device_id, payload):
        self.tag = tag
        self.device_id = device_id
        self.timestamp = timestamp
        self.payload = payload

    @staticmethod
    def from_json(device_key):
        # "tag": "ufficio",
        #  "timestamp_device": "2020-03-12T16:00:04",
        #  "device_id": "dev-4qxyl1t5bjep",
        #  "payload": {
        #         "temp": 20,
        #         "pressure": 57
        #  }
        return DataTag(device_key["tag"], device_key["timestamp_device"], device_key["device_id"], device_key["payload"])

    def __str__(self):
        return "DataTag: tag: {}, devid:{}, payload :{}".format(self.tag, self.device_id, self.payload)

    @property
    def Tag(self):
        return self.tag

    @property
    def Timestamp(self):
        return self.timestamp

    @property
    def DeviceId(self):
        return self.device_id

    @property
    def Payload(self):
        return self.payload
