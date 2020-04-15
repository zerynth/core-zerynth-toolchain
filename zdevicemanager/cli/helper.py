import click
import zdevicemanager
from functools import wraps
from zdevicemanager.base.base import error

from ..client.client import ZdmClient

pass_adm = click.make_pass_decorator(ZdmClient, ensure=True)



def handle_error(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
             return f(*args, **kwargs)
        except zdevicemanager.client.errors.ForbiddenError as e:
            error("Access Denied. Run the command [zdm login]")
        except zdevicemanager.client.errors.NotFoundError as err:
            error("{}. {}.".format(err.title, err.msg))
        except zdevicemanager.client.errors.APIError as err:
            error("Internal Server error. Details: {}.".format(err.msg))
        except zdevicemanager.client.errors.ZdmException as err:
            error("ZDM general error. Details: {}.".format(err.message))
        except Exception as e:
            error("Unknown error. {}".format(e))
    return wrapper
