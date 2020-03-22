from datetime import datetime

from .base import Model, Collection


class ChangeSetModel(Model):

    @property
    def version(self):
        ver = self.attrs.get("version")  # timestamp im milliseconds
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
