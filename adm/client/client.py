from .models.workspacetest import WorkspaceCollection
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
