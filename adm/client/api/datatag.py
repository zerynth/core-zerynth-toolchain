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

        url = self._url("/tsmanager/workspace/{0}/tag", workspace_id)
        res = self._get(url)
        self._raise_for_status(res)
        return res