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
        return "Device: id: {}, name:{}, fleetid :{}".format(self.id, self.name, self.fleet_id)

    @property
    def Id(self):
        return self.id

    @property
    def FleetID(self):
        return self.fleet_id

    def add_key(self, device_key):
        self.keys.append(device_key)
