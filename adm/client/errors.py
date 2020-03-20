import requests


class ZdmException(Exception):
    """
     A base class from which all other exceptions inherit.

     If you want to catch all errors that the ZDM SDK might raise,
     catch this base exception.
     """


def create_api_error_from_http_exception(e):
    """
    Create a suitable APIError from requests.exceptions.HTTPError.
    """
    response = e.response
    try:
        # TODO: use err_code, err_title and err_mesage of the ZDM API
        explanation = response.json()['message']
    except ValueError:
        explanation = (response.content or '').strip()
    cls = APIError
    if response.status_code == 403:
        cls = ForbiddenException
    if response.status_code == 404:
        # if explanation and ('No such image' in str(explanation) or
        #                     'not found: does not exist or no pull access'
        #                     in str(explanation) or
        #                     'repository does not exist' in str(explanation)):
        #     cls = ImageNotFound
        # else:
        cls = NotFoundError
    raise cls(e, response=response, explanation=explanation)


class APIError(requests.exceptions.HTTPError, ZdmException):
    """
    An HTTP error from the API.
    """
    def __init__(self, message, response=None, explanation=None):
        # requests 1.2 supports response as a keyword argument, but
        # requests 1.1 doesn't
        super(APIError, self).__init__(message)
        self.response = response
        self.explanation = explanation

    def __str__(self):
        message = super(APIError, self).__str__()

        if self.is_client_error():
            message = '{0} Client Error: {1}'.format(
                self.response.status_code, self.response.reason)

        elif self.is_server_error():
            message = '{0} Server Error: {1}'.format(
                self.response.status_code, self.response.reason)

        if self.explanation:
            message = '{0} ("{1}")'.format(message, self.explanation)

        return message

    @property
    def status_code(self):
        if self.response is not None:
            return self.response.status_code

    def is_error(self):
        return self.is_client_error() or self.is_server_error()

    def is_client_error(self):
        if self.status_code is None:
            return False
        return 400 <= self.status_code < 500

    def is_server_error(self):
        if self.status_code is None:
            return False
        return 500 <= self.status_code < 600


class ForbiddenException(APIError):
    pass


class NotFoundError(APIError):
    """Raised when a resource is not found
    """
    pass
