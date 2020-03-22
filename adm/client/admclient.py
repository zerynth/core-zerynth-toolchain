from base.zrequests import zget, zpost, zput, zdelete

from .errors import NotFoundError
from .logging import MyLogger
from .models import Gate

logger = MyLogger().get_logger()


class ADMClient(object):
    """
    A client for communicating with the API of ADM.
    Example:
        >>> import adm
        >>> client = adm.ADMClient()

    """

    def __init__(self, gates_url="http://api.localhost/v1/gate",
                 ):
        self.gate_url = gates_url

    ##############################
    #   Gate: WebHook
    ##############################


    def gate_delete(self, gate_id):
        path = self.urljoin(self.gate_url, gate_id)
        logger.debug("Deleting gate : {}".format(path))
        try:
            res = zdelete(path)
            if res.status_code == 200:
                return "Gate deleted succesfully"
            else:
                return None
        except Exception as e:
            print(e)

    def urljoin(self, base_path, *args):
        """
        Joins given arguments into an url. Trailing but not leading slashes are
        stripped for each argument.

        Example
           urljoin("hello",  "world"))   ->  hello/world
           urljoin("/hello",  "world")   -> /hello/world
           urljoin("hello/",  "world")   -> hello/world
           urljoin("hello/",  "world/")   -> hello/world
           urljoin("hello/",  "/world/")  ->  hello//world
        """

        # return "/".join(map(lambda x: str(x).rstrip('/'), args))
        return base_path + "/".join(map(lambda x: str(x).rstrip('/'), args))
