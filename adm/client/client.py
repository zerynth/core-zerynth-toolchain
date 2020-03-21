from .api.client import APIClient
from .models.datatag import DataTagCollection
from .models.device import DeviceCollection
from .models.devicekey import DeviceKeyCollection
from .models.fleet import FleetCollection
from .models.job import JobCollection
from .models.workspacetest import WorkspaceCollection


class ZdmClient(object):

    def __init__(self, *args, **kwargs):
        self.api = APIClient(*args, **kwargs)

    @property
    def workspaces(self):
        """
        An object for managing workspaces on the server.
        """
        return WorkspaceCollection(client=self)

    @property
    def devices(self):
        """
        An object for managing devices on the server.
        """
        return DeviceCollection(client=self)

    @property
    def fleets(self):
        """
        An object for managing fleets on the server.
        """
        return FleetCollection(client=self)

    @property
    def data(self):
        """
        An object for managing the data sent by the devices on the server.
        """
        return DataTagCollection(client=self)

    @property
    def keys(self):
        """
        An object for managing the keys of the devices on the server.
        """
        return DeviceKeyCollection(client=self)

    @property
    def jobs(self):
        """
        An object for managing the jobs.
        """
        return JobCollection(client=self)
