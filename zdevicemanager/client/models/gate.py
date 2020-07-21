from .base import Model, Collection


class GateModel(Model):

    @property
    def period(self):
        return self.attrs.get("period")

    @property
    def status(self):
        return self.attrs.get("status")

    @property
    def is_enabled(self):
        return self.attrs.get("status") == "active"

    @property
    def is_disabled(self):
        return self.attrs.get("status") == "disabled"

    @property
    def last_time_scheduled(self):
        return self.attrs.get("last_time_schedule")

    @property
    def type(self):
        return self.attrs.get("type")

    @property
    def origin(self):
        return self.attrs.get("origin")

    @property
    def configuration(self):
        return self.attrs.get("configuration")


class GateCollection(Collection):
    model = GateModel

    def list(self, workspace_id, status, gtype):
        """
        List all gates of a workspace.
        """
        resp = self.client.api.gates(workspace_id, status, gtype)
        return [self.prepare_model(r) for r in resp]

    def get(self, gate_id):
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

    def delete(self, gate_id):
        return self.client.api.delete_gate(gate_id)

    def enable(self, gate_id):
        return self.client.api.update_gate_status(gate_id, "active")

    def disable(self, gate_id):
        return self.client.api.update_gate_status(gate_id, "disabled")

    def update_gate_status(self, gate_id, status):
        """
        Upadate a gate's status.

        Args:
            gate_id (str): The id of the gate.
            status (str): "active", "disabled".
        Returns:
            (:py:class:`GateModel`): The gate.
        Raises:
            :py:class:`zdm.errors.NotFound`
                If the image does not exist.
            :py:class:`zdm.errors.APIError`
                If the server returns an error.
        """
        return self.prepare_model(self.client.api.update_gate_status(gate_id, status))


class WebhookGateModel(GateModel):

    @property
    def configuration_tags(self):
        return self.attrs.get("configuration").get("payload").get("tags")


class WebhookGateCollection(GateCollection):
    model = WebhookGateModel

    def create(self, name, url, token, period, workspace_id, tags, fleets, origin):
        """
        Create a webhook gate.

        Args:
            name (str): name of the gate.
            url(str): url of the webhook
            token(str): optional token for the webhook
            period(int): interval for webhook requests
            workspace_id(str): workspace id
            tags(str[]): optional tags filter
            fleets(str[]): optional fleets filter

        Returns:
            A :py:class:`GateModel` object.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        resp = self.client.api.create_webhook(name, url, token, period, workspace_id, tags, fleets, origin)
        return resp['id']  # self.prepare_model(resp)

    def update(self, gate_id, name=None, period=None, url=None, tokens=None, tags=None, fleets=None):
        resp = self.client.api.update_webhook(gate_id, name, period, url, tokens, tags, fleets)
        return resp

class ExportGate(GateModel):

    @property
    def cron(self):
        return self.attrs.get("configuration").get("cron")


class ExportGateCollection(GateCollection):
    model = ExportGate

    def create(self, name, dump_name, workspace_id, email, type="json", frequency="now", day="", tags=None, fleets=None):
        """
        Create an export gate.
        """

        resp = self.client.api.create_export_gate(name, dump_name, type, frequency, day, workspace_id, email, tags,
                                                  fleets)
        return resp['id']

    def update(self, gate_id, name=None, cron=None, dump_type=None, emails=None, tags=None):
        resp = self.client.api.update_export_gate(gate_id, name, cron, dump_type, emails, tags)
        return resp

class AlarmGate(GateModel):

    @property
    def tags(self):
        return self.attrs.get("configuration").get("tags")


class AlarmGateCollection(GateCollection):
    model = AlarmGate

    def create(self, name, workspace_id, tags, threshold, email):
        """
        Create an alarm gate
        :param name: the gate name
        :param workspace_id: the workspace id
        :param tags: the condition tags (string array)
        :param threshold: the minimum duration of a condition to be notified when it is opened
        :param email: the email where to receive notifications
        :return: id, the uuid of the created gate
        """
        resp = self.client.api.create_alarm_gate(name, workspace_id, tags, threshold, email)
        return resp['id']

    def update(self, gate_id, name=None, tags=None, threshold=None):
        resp = self.client.api.update_alarm_gate(gate_id, name, tags, threshold)
        return resp
