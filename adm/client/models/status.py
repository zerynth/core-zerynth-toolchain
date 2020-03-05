class Status:
    """Status class of """

    def __init__(self, name, value, time):
        self.name = name
        self.value = value
        self.timestamp = time

    # {'status': {'@fota': {'v': {'on_schedule': '', 'fw_version': '7.0'}, 't': 1583407687328}}}

    # @staticmethod
    # def from_json(status):
    #     return Status("s", status['v'], status['t'])

    def __str__(self):
        return "Status <id: {}, name:{}, version :{}, key:{}, value:{}>".format(self.id, self.version, self.key, self.value)

    def is_fota(self):
        return self.name == "@fota"

    @property
    def Name(self):
        return self.name

    @property
    def Value(self):
        return self.value
