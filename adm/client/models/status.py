from datetime import datetime

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
        return "Status <name:{}, value :{}, timestamp:{}>".format(self.name, self.value, self.timestamp)

    def is_fota(self):
        return self.name == "@fota"

    def is_private(self):
        return self.name.startswith("_")

    def is_job(self):
        return self.name.startswith("@")

    @property
    def Name(self):
        return self.name

    @property
    def Value(self):
        return self.value

    @property
    def Timestamp(self):
        # if you encounter a "year is out of range" error the timestamp
        # may be in milliseconds
        ts = self.timestamp / 1000
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
