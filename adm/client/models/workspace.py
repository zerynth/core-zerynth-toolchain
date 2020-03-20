import json
from .fleet import Fleet

class Workspace:
    """Workspace class represent a device"""

    def __init__(self, id, name, fleets=[], account_id=None, description=""):
        self.id = id
        self.name = name
        self.account_id = account_id
        self.fleets = fleets
        self.description = description

    @staticmethod
    def from_json(wks):
        fleets = []
        if wks['fleet'] is not None:
            fleets = [Fleet(fleet["id"], fleet["name"], fleet["workspace_id"] if fleet["workspace_id"] is not "" else None, []) for fleet in wks['fleet']]
        return Workspace(wks["id"], wks["name"], fleets, wks["account_id"] if wks["account_id"] is not "" else None, wks["description"])

    def __str__(self):
        return "Workspace: id: {}, name:{}, account:{}".format(self.id, self.name, self.account_id)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @property
    def Description(self):
        return self.description

    @property
    def Name(self):
        return self.name

    @property
    def Id(self):
        return self.id

    @property
    def Fleets(self):
        return self.fleets

