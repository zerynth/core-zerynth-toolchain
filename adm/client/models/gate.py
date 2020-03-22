from .base import Model, Collection


class GateModel(Model):

    @property
    def period(self):
        return self.attrs.get("period")

    @property
    def status(self):
        return self.attrs.get("status")

    @property
    def last_time_scheduled(self):
        return self.attrs.get("last_time_schedule")

    @property
    def type(self):
        return self.attrs.get("type")


class GateCollection(Collection):
    model = GateModel

    def list(self, workspace_id, status, origin):
        """
        List all gates of a workspace.
        """
        resp = self.client.api.gates(workspace_id, status, origin)
        return [self.prepare_model(r) for r in resp]

    def create_webhook(self, name, url, token, period, workspace_id, tag):
        """
        Create a webhook gate.

        Args:
            name (str): name of the gate.

        Returns:
            A :py:class:`GateModel` object.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.create_webhook(name, url, token, period, workspace_id, tag)
        return resp['id']  # self.prepare_model(resp)

    def get_webhook(self, gate_id):
        """
        GetS an webhook gate.

        Args:
            gate_id (str): The id of the gate.
        Returns:
            (:py:class:`GateModel`): The gate.
        Raises:
            :py:class:`zdm.errors.NotFound`
                If the image does not exist.
            :py:class:`zdm.errors.APIError`
                If the server returns an error.
        """
        return self.prepare_model(self.client.api.get_webhook(gate_id))

    def update_webhook(self, gate_id, name=None, status=None, period=None, url=None):
        """
        Upadate an webhook gate.

        Args:
            gate_id (str): The id of the gate.
            name (str): The name. Default None
            status (str): "active", "disabled.
            periiod (int): Every in Seconds.
            url (str): Url of the webhook.
        Returns:
            (:py:class:`GateModel`): The gate.
        Raises:
            :py:class:`zdm.errors.NotFound`
                If the image does not exist.
            :py:class:`zdm.errors.APIError`
                If the server returns an error.
        """
        return self.prepare_model(self.client.api.update_webhook(gate_id, name, status, period, url))


    def delete_webhook(self, gate_id):
        return self.client.api.delete_webhook(gate_id)
