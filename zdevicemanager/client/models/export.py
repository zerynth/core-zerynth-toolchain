from .base import Model, Collection


class ExportModel(Model):

    @property
    def Name(self):
        return self.attrs.get("name")

    @property
    def Type(self):
        return self.attrs.get("dump_type")

    @property
    def Url(self):
        return self.attrs.get("dump_url")

    @property
    def Status(self):
        return self.attrs.get("status")

    @property
    def WorkspaceId(self):
        return self.attrs.get("configurations").get("workspace_id")

    @property
    def Configurations(self):
        return self.attrs.get("configurations")

    @property
    def Notifications(self):
        return self.attrs.get("notifications")


class ExportsCollection(Collection):
    model = ExportModel

    def create(self, name,  workspace_id, type="json", emails=[], tags=None, fleets=None, start=None, end=None):
        """
        Create a dump request
        """
        resp = self.client.api.create_export(name, workspace_id, type, emails, tags, fleets, start, end)
        return self.prepare_model(resp)

    def get(self, id):
        """
        Get a dump by ID.
        """
        resp = self.client.api.get_export(id)
        return self.prepare_model(resp)