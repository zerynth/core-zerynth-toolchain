from datetime import datetime

from .base import Model, Collection


class ChangeSetModel(Model):

    @property
    def version(self):
        ver = self.attrs.get("version") # timestamp im milliseconds
        ver /= 1000
        return datetime.utcfromtimestamp(ver).strftime('%Y-%m-%d %H:%M:%S')

    @property
    def key(self):
        return self.attrs.get("key")

    @property
    def value(self):
        return self.attrs.get("value")

    @property
    def target(self):
        return self.attrs.get("target")


class ChangeSetCollection(Collection):
    model = ChangeSetModel

    def create(self, key, value, targets):
        """
        Create a new changeset

        Args:
            key (str): Key of the changeset.
            value (str): Value of the changeset.
            targets (list): Targets of the changeset (devices).

        Returns:
            A :py:class:`ChangeSetModel` object.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        id = self.client.api.create_changeset(key, value, targets)
        return id  # self.prepare_model(resp)


class ChangeSet:
    """ChangeSet class represent a chengeset"""

    def __init__(self, id, version, key, value, space, owner, target):
        self.id = id
        self.key = key
        self.version = version
        self.value = value  # json
        self.owner = owner
        self.target = target

    # "status": {
    #     "ChangeId": "e683b6a6-f75e-45fb-bd34-784d4f42082c",
    #     "Key": "$fota$",
    #     "Owner": "f_AJewukTfawU7UHJ0pIBg",
    #     "OwnerType": "user",
    #     "Space": "W",
    #     "Target": "dev-4pc2ycnlob9h",
    #     "TargetType": "device",
    #     "Value": {
    #         "url": "http://api.adm.zerinth.com/v1/workspace/wks-4pc4a2v05zpd/firmware/firm4pc4g0ex5nnm/download",
    #         "version": "0.1"
    #     },
    #     "Version": 1582731156755
    # }
    @staticmethod
    def from_json(chset):
        return ChangeSet(chset["ChangeId"], chset["Version"], chset["Key"], chset["Value"], chset["Space"],
                         chset["Owner"], chset["target"])

    def __str__(self):
        return "ChangeSet <id: {}, name:{}, version :{}, key:{}, value:{}>".format(self.id, self.version, self.key,
                                                                                   self.value)

    @property
    def Id(self):
        return self.id

    @property
    def Version(self):
        return self.version

    @property
    def Key(self):
        return self.key

    @property
    def Value(self):
        return self.value
