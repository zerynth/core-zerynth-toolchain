from ..constants import STATUS_KEY_PRIVATE, STATUS_KEY_STRONG_PRIVATE
from ..errors import ZdmException


class ExportsApiMixin(object):

    def create_export(self, name,  workspace_id, type="json", emails=[], tags=None, fleets=None, start=None, end=None):
        """
        Create a new export.

        Args:
            name (str): The name of the export
            type (str): the type of th export ["json", "csv"]
            workspace_id (str): the workspace_id to export the data
            emails (list str): the emails to be informed when the export is ready
            tags (list of str): list of tags
            fleets (list of str): list of fleets

        Returns:
            id (str). The id of the created export

        Raises:
            :py:class:`zdm.errors.APIError`
                If the server returns an error.
        """

        payload = {
            "name": name,
            "dump_type": type,
            "configurations": {
                "workspace_id": workspace_id,
                "start": start,
                "end": end,
                "tags": tags,
                "fleets": fleets
            },
            "notifications": {
                "emails": emails
            }
        }

        url = self._url("/dump/")
        res = self._result(self._post(url, data=payload))
        return res["dump"]

    def get_export(self, export_id):
        """
        Returns an export

        Args:
            export_id (str): The export id.
        Returns:
            (dicts): a dict containing the export's information

        Raises:
            :py:class:`zdm.errors.APIError`
                If the server returns an error.
        """
        res = self._result(self._get(self._url("/dump/{0}", export_id)))
        return res["dump"]
