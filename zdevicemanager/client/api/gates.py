class GateApiMixin(object):

    def gates(self, workspace_id, status="active", origin="data"):
        """
        Get all the gates associated to a workspace.

        Args:
            workspace_id (str): the workspace Id.
            status (str): Filter gates by status ['active', 'disabled']. Default "active".
            origin (str): Filter gates by origin. ['data', 'events]. Default "data".

        Returns:
            (list of dicts): a list of dictionaries

        Raises:
            :py:class:`zdevicemanager.errors.APIError`
                If the server returns an error.
        """
        params = {"status": status, "origin": origin}
        u = self._url("/gate/workspace/{0}", workspace_id)
        res = self._result(self._get(u, params=params))
        return res["gates"] if "gates" in res and res["gates"] is not None else []

    def get_webhook(self, gate_id):
        """
        Get detailed information about a webhook by ID.

        Args:
            gate_id (str): The gate id.

        Returns:
            (dict): a dictionary of details

        Raises:
            :py:class:`zdevicemanager.errors.APIError`
                If the server returns an error.
        """
        res = self._result(self._get(self._url("/gate/{0}/", gate_id)))
        return res["gate"]

    def create_webhook(self, name, url, token, period, workspace_id, tag):
        """
        Create e new gate.

        Args:
           device_id (str): The gate id to get

        Returns:
           (dict): a dictionary of details

        Raises:
           :py:class:`zdevicemanager.errors.APIError`
               If the server returns an error.
        """
        payload = {"name": name,
                   "url": url,
                   "content-type": "application/json",
                   "period": period,
                   "origin": "data",
                   "payload": {
                       "tag": tag,
                       "workspace_id": workspace_id},
                   "tokens": {
                       "X-Auth-Token": token
                   }
                   }
        u = self._url("/gate/webhook/")
        res = self._result(self._post(u, data=payload))
        return res

    def update_webhook(self, gate_id, name=None, status=None, period=None, url=None):
        """
       Update a webhook gate.

       Args:
          device_id (str): The gate id to get
          name (str): the new name of the gate
          fleet_id (str): the fleet id to be assigned [Default: None]

       Returns:
          (dict): a dictionary of details

       Raises:
          :py:class:`zdevicemanager.errors.APIError`
              If the server returns an error.
       """
        payload = {}
        if name:
            payload["name"] = name
        if status:
            payload["status"] = status
        if period:
            payload["period"] = period
        if url:
            payload["url"] = url

        u = self._url("/gate/{0}/", gate_id)
        res = self._result(self._put(u, data=payload))
        return res


    def delete_webhook(self, gate_id):

        u = self._url("/gate/{0}/", gate_id)
        res = self._result(self._delete(u))
        return res