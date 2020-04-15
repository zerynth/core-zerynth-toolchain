from .base import Model, Collection


class EventModel(Model):

    @property
    def Name(self):
        return self.attrs.get("name")

    @property
    def Timestamp(self):
        return self.attrs.get("created_at")

    @property
    def DeviceId(self):
        return self.attrs.get("device_id")

    @property
    def Payload(self):
        return self.attrs.get("payload")


class EventCollection(Collection):
    model = EventModel

    def get(self, workspace_id, device_id=None, start=None, end=None, page=None, size=None, sort=None):
        """
        Get all the data associated to a tag
        """
        resp = self.client.api.get_events(workspace_id, device_id, start, end)
        return [self.prepare_model(event) for event in resp]

