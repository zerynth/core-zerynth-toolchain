from .base import Collection
from .changeset import ChangeSetModel


class JobModel(ChangeSetModel):
    @property
    def name(self):
        # delete the "@" at the begining of the key
        return self.convert_job_to_name(self.key)

    @staticmethod
    def convert_name_into_job(name):
        if not name.startswith('@'):
            name = "@" + name
        return name

    @staticmethod
    def convert_job_to_name(name):
        if name.startswith('@'):
            return name[1:]
        return name


class JobCollection(Collection):
    model = JobModel

    def schedule(self, name, args, targets, on_time=None):
        """
        Schedule a new Job

        Args:
            name (str): Name of the job.
            args (dict): Arguments of the job as key, value.
            targets (list): Targets of the changeset (devices).

        Returns:
            A :py:class:`JobModel` object.

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        value = {"args": args,
                 "on_schedule": on_time}
        key = JobModel.convert_name_into_job(name)
        id = self.client.api.create_changeset(key, value, targets)
        return id

    def status(self, name, device_id):
        status = self.client.api.get_current_device_status(device_id)
        mstatus = [self.prepare_model(s) for s in status]
        for s in mstatus:
            if s.name == name:
                return s
        return None
