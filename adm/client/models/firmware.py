class Firmware:
    """Identify a firmware """

    def __init__(self, id, version, workspace_id):
        self.id = id
        self.version = version
        self.workspace_id = workspace_id


    @staticmethod
    def from_json(firmware):
            # {'firmware': {  'Metadata': {'metadata': 34},
            #                 'Description': '',
            #                 'Id': 'firm4q1sgv5fv5e4',
            #                 'CreatedAt': '2020-03-03T15:28:18.866792255Z',
            #                 'WorkspaceId': 'wks-4pxge15hkfew',
            #                 'Firmware':
            #                 'AccountId': 'OsbDq5jtSwmmPi5I5bNyYw',
            #                 'Version': '1.6'}}
            return Firmware(firmware["id"], firmware["version"], firmware["workspace_id"])

    def __str__(self):
        return "firmware: id: {}, version:{}, workspaceID :{}".format(self.id, self.version, self.workspace_id)

    @property
    def Id(self):
        return self.id

    @property
    def Version(self):
        return self.version

    @property
    def WorkspaceID(self):
        return self.workspace_id