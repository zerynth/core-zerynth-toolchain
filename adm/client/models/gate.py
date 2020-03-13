#
# class Gate(Model):
#     """
#     An Gate on the server.
#     """
#     def __repr__(self):
#         return "<%s: '%s'>" % (self.__class__.__name__, "', '".join(self.tags))
#
# class GateCollection(Collection):
#
#     model = Gate
#
#     def get(self, name):
#         """
#         Gets an ate.
#         Args:
#             name (str): The id of the gate.
#         Returns:
#             (:py:class:`Gate`): The gate.
#         Raises:
#             :py:class:`docker.errors.ImageNotFound`
#                 If the image does not exist.
#             :py:class:`docker.errors.APIError`
#                 If the server returns an error.
#         """
#         return self.prepare_model(self.client.api.inspect_image(name))

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
