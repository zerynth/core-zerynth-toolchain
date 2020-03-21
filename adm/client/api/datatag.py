class DataApiMixin(object):

    def tags(self, workspace_id):
        """
        Return all the tags of a workspace

        Args:
            workspace_id (str): The  workspace id

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """

        url = self._url("/tsmanager/workspace/{0}/tags", workspace_id)
        res = self._result(self._get(url))
        return res["tags"] if "tags" in res and res["tags"] is not None else []

    def get_data(self, workspace_id, tag, device_id=None, custom=None, start=None, end=None, page=None, per_page=None, sort=None):
        """
        Get all data associated to a tag in a workspace.

        Args:
            workspace_id (str): the  workspace id
            tag (str): the name of the tag
            device_id (str): [optional] the device id

        Raises:
            :py:class:`zdm.errors.APIError`
                If the server returns an error.
        """
        # TODO: filter with start date and other filters
        params = {
            "start": "2006-01-02 15:04"
            # "devid"
            # "custom"
            # "end"
            # "page"
            # "per_page":
            # "sort"
        }
        url = self._url("/tsmanager/workspace/{0}/tag/{1}", workspace_id, tag)
        res = self._result(self._get(url, params=params))
        return res["result"] if "result" in res and res["result"] is not None else []
