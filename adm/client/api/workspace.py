class WorkspaceApiMixin(object):

    def containers(self, all=False, limit=-1, size=False, filters=None):
        u = self._url("/workspace/")
        res = self._result(self._get(u))
        return res["workspaces"]

    # @utils.check_resource('image')
    def get_workspace(self, workspace):
        """
        Get detailed information about a workspace.

        Args:
            workspace (str): The workspace to get

        Returns:
            (dict): a dictionary of details

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        res = self._result(self._get(self._url("/workspace/{0}", workspace)))
        return res["workspace"]

    def create_workspace(self, name, description=""):
        data = {"name": name, "description": description}
        u = self._url("/workspace/")
        res = self._result(self._post(u, data=data))
        return res["workspace"]