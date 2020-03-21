from .models.workspacetest import WorkspaceCollection
from .models.datatag import DataTagCollection
from .models.device import DeviceCollection
from .api.client import APIClient

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
    def data(self):
        return DataTagCollection(client=self)