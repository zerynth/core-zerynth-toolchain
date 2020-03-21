class StatusApiMixin(object):

    def create_changeset(self, key, value, targets):
        """
        Return all the tags of a workspace

        Args:
            key (str): The key of the changeset.
            value (json): The Value to be associated to the key.
            targets (list of str): List of targets of the changest.

        Retunrs:
            id (str). The id of the created changeset

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        payload = {"key": key,
                   "value": value,
                   "targets": targets}
        url = self._url("/status/changeset")
        res = self._result(self._post(url, data=payload))
        return res["id"]

    def get_current_device_status(self, device_id):
        """
        Return the current status of the device. It includes all the changeset
        sent by the device to the zdm.

        Args:
            device_id (str): The device id.

        Returns:
            (list of dicts): a list of changesets

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.

        Example:
            >>> from adm import ZdmClient
            >>> c = ZdmClient(base_url="api.zdm.stage.zerynth.com")
            >>> dev = zcli.adm.devices.create("mydev")
            >>> c.get_current_device_status(dev.id)
             [
                {
                    "key": "@fota":
                    "value: { },
                    "version": 1582731641910
                },
                {
                    "key": "__manifest":
                    "value: { },
                    "version": 1582731641910
                }
             ]
        """

        u = self._url("/status/currentstatus/{0}", device_id)
        res = self._result(self._get(u))
        status = []
        if "status" in res:
            for key, value in res["status"].items():
                status.append({"key": key, "value": value['v'], "version": value['t']})
        return status

    # def _get_current_device_status(self, device_id):
    #     # /status/currentstatus/{devid}
    #     path = "{}currentstatus/{}".format(self.status_url, device_id)
    #     logger.debug("Get the current status of {} device: {}".format(device_id, path))
    #     r = zget(path)
    #     if r.status_code == 200:
    #         data = r.json()
    #         datastatus = data['status'] if "status" in data and data["status"] and not None else {}
    #         status = []
    #         for key, value in datastatus.items():
    #             s = Status(key, value['v'], value['t'])
    #             status.append(s)
    #         return status
    #     else:
    #         logger.error("Error in creating the changeset {}, {}".format(r.status_code, r.text))
    #         raise NotFoundError(r.text)
