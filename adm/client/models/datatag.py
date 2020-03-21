from .base import Model, Collection


class DataTagModel(Model):

    @property
    def Tag(self):
        return self.attrs.get("tag")

    @property
    def Timestamp(self):
        return self.attrs.get("timestamp_device")

    @property
    def DeviceId(self):
        return self.attrs.get("device_id")

    @property
    def Payload(self):
        return self.attrs.get("payload")


class DataTagCollection(Collection):
    model = DataTagModel

    def list(self, workspace_id, page=None, page_size=None, sort=None):
        """
        List tags available in a workspace
        """
        resp = self.client.api.tags(workspace_id)
        return resp

    def get(self, workspace_id, tag, device_id=None, start=None, end=None, page=None, per_page=None, sort=None):
        """
        Get all the data associated to a tag
        """
        resp = self.client.api.get_data(workspace_id, tag, device_id, page, per_page, sort)
        return [self.prepare_model(datatag) for datatag in resp]


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
        return DataTag(device_key["tag"], device_key["timestamp_device"], device_key["device_id"],
                       device_key["payload"])

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
