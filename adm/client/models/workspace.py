import json
from .fleet import Fleet

class Workspace:
    """Workspace class represent a device"""

    def __init__(self, id, name, fleets=[], account_id=None):
        self.id = id
        self.name = name
        self.account_id = account_id
        self.fleets = fleets

    @staticmethod
    def from_json(wks):
        # {"Workspace":{"id":"wks-4lvz89ccmepv", "name":"doName","account_id":"", "description":"","fleets":null,"created_at":"2020-01-21T15:49:39.230924Z"}}
        # wks = json["workspace"]
        # {'id': 'wks-4p8azofi7ton', 'description': '', 'created_at': '2020-02-24T09:09:03.837579Z', 'name': 'prova 4', 'fleet': None, 'account_id': 'OsbDq5jtSwmmPi5I5bNyYw'
        fleets = [Fleet(fleet["id"], fleet["name"], fleet["workspace_id"] if fleet["workspace_id"] is not "" else None, []) for fleet in wks['fleet']]
        return Workspace(wks["id"], wks["name"], fleets, wks["account_id"] if wks["account_id"] is not "" else None)

    def __str__(self):
        return "Workspace: id: {}, name:{}, account:{}".format(self.id, self.name, self.account_id)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @property
    def Name(self):
        return self.name

    @property
    def Id(self):
        return self.id

    @property
    def Fleets(self):
        return self.fleets