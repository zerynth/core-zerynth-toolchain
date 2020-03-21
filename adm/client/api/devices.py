class DeviceApiMixin(object):

    def devices(self):
        """
        Get all the devices

        Returns:
            (list of dicts): a list of dictionaries

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        u = self._url("/device/")
        res = self._result(self._get(u))
        return res["devices"]

    # @utils.check_resource('image')
    def get_device(self, device_id):
        """
        Get detailed information about a device by ID.

        Args:
            device_id (str): The device id to get

        Returns:
            (dict): a dictionary of details

        Raises:
            :py:class:`adm.errors.APIError`
                If the server returns an error.
        """
        res = self._result(self._get(self._url("/device/{0}", device_id)))
        return res["device"]

    def create_device(self, name, fleet_id=None):
        """
        Create e new device.

        Args:
           device_id (str): The device id to get

        Returns:
           (dict): a dictionary of details

        Raises:
           :py:class:`adm.errors.APIError`
               If the server returns an error.
        """
        payload = {
             "name": name,
             "fleet_id": None if fleet_id is None else fleet_id
        }
        u = self._url("/device/")
        res = self._result(self._post(u, data=payload))
        return res["device"]

    def update_device(self, device_id, name, fleet_id=None):
        """
       Update a  device.

       Args:
          device_id (str): The device id to get
          name (str): the new name of the device
          fleet_id (str): the fleet id to be assigned [Default: None]

       Returns:
          (dict): a dictionary of details

       Raises:
          :py:class:`adm.errors.APIError`
              If the server returns an error.
       """
        payload = {
            "name": name,
            "fleet_id": None if fleet_id is None else fleet_id
        }
        u = self._url("/device/{0}/", device_id)
        res = self._result(self._put(u, data=payload))
        return res
