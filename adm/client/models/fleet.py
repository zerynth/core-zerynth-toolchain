from .device import Device
from .base import Model, Collection

class FleetModel(Model):
    """Fleet class represent a Fleet"""

    pass

class FleetCollection(Collection):
    model = FleetModel

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
