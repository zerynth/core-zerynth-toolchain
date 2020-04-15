class EventApiMixin(object):

    def get_events(self, workspace_id, device_id=None, start=None, end=None):
        """
        Get all events in a workspace.

        Args:
            workspace_id (str): the  workspace id
            device_id (str): [optional] the device id

        Raises:
            :py:class:`zdm.errors.APIError`
                If the server returns an error.
        """

        params = {
            "start": start,
            "devid": device_id,
            "end": end,
            "sort": "-created_at"
        }

        url = self._url("/tsmanager/workspace/{0}/event", workspace_id)
        res = self._result(self._get(url, params=params))
        return res["events"] if "events" in res and res["events"] is not None else []
