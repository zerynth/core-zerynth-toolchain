from functools import partial

import requests
import six
from base.zrequests import zget, zpost

from .workspace import WorkspaceApiMixin
from .datatag import DataApiMixin
from ..constants import DEFAULT_TIMEOUT_SECONDS, DEFAULT_USER_AGENT, DEFAULT_ZDM_API_VERSION
from ..errors import create_api_error_from_http_exception

class APIClient(requests.Session, WorkspaceApiMixin, DataApiMixin):
    """
    A low-level client for the ZDM API
    """

    def __init__(self, base_url=None, version=None,
                 timeout=DEFAULT_TIMEOUT_SECONDS, tls=False,
                 user_agent=DEFAULT_USER_AGENT, num_pools=None,
                 credstore_env=None):
        super(APIClient, self).__init__()

        if version is None:
            self._version = DEFAULT_ZDM_API_VERSION
        else:
            self._version = version
        self.base_url = base_url
        self.timeout = timeout
        self.headers['User-Agent'] = user_agent

    # @update_headers
    def _get(self, url, **kwargs):
        return zget(url, **kwargs)
        # return self.get(url, **self._set_request_timeout(kwargs))

    def _post(self, url, **kwargs):
        return zpost(url, **kwargs)

    def _set_request_timeout(self, kwargs):
        """Prepare the kwargs for an HTTP request by inserting the timeout
        parameter, if not already present."""
        kwargs.setdefault('timeout', self.timeout)
        return kwargs

    def _url(self, pathfmt, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, six.string_types):
                raise ValueError(
                    'Expected a string but found {0} ({1}) '
                    'instead'.format(arg, type(arg))
                )

        quote_f = partial(six.moves.urllib.parse.quote, safe="/:")
        args = map(quote_f, args)

        #if kwargs.get('versioned_api', True):
        return '{0}/v{1}{2}'.format(
                self.base_url, self._version, pathfmt.format(*args)
            )
        #else:
        #    return '{0}{1}'.format(self.base_url, pathfmt.format(*args))

    def _raise_for_status(self, response):
        """Raises stored :class:`APIError`, if one occurred."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise create_api_error_from_http_exception(e)

    def _result(self, response, json=True):
        self._raise_for_status(response)
        if json:
            return response.json()
        return response.text
