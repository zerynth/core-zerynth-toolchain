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

class Gate:
    """Gate class represent a gate"""

    def __init__(self, id, name, period, status, gate_type, origin, configuration, last_time_schedule):
        self.id = id
        self.name = name
        self.period = period
        self.status = status
        self.type = gate_type
        self.origin = origin
        self.configuration = configuration
        self.last_schedule = last_time_schedule

        # ID               string          `json:"id" pg:",pk"`
        # Name             string          `json:"name" pg:",notnull"`
        # Period           int             `json:"period" pg:",notnull"`
        # Status           string          `json:"status" pg:",notnull"`
        # Type             string          `json:"type" pg:",notnull"`
        # Origin           string          `json:"origin" pg:",notnull"`
        # AccountId        string          `json:"account_id" pg:",notnull"`
        # Configuration    json.RawMessage `json:"configuration"`
        # LastTimeSchedule time.Time       `json:"last_time_schedule"`

    @staticmethod
    def from_json(gate):
        print(gate["last_time_schedule"])
        return Gate(gate["id"], gate["name"], gate["period"], gate["status"], gate["type"], gate["origin"],
                    gate['configuration'], gate["last_time_schedule"])

    def __str__(self):
        return "Gate: id: {}, name:{}, schedule :{}".format(self.id, self.name, self.LastSchedule)

    @property
    def Id(self):
        return self.id

    @property
    def Name(self):
        return self.name

    @property
    def Period(self):
        return self.period

    @property
    def Status(self):
        return self.status

    @property
    def LastTimeSchedule(self):
        # TODO calling LastTimeSChedul in a object return none, wihile with last_schedule is working
        self.last_schedule
