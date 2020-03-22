import click
import adm
from functools import wraps
from base.base import error

from ..client.client import ZdmClient

pass_adm = click.make_pass_decorator(ZdmClient, ensure=True)



def handle_error(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
             return f(*args, **kwargs)
        except adm.client.errors.ForbiddenException as e:
            error("Access Denied. Run the command [zdm login]")
        except adm.client.errors.NotFoundError as err:
            error("{}. {}.".format(err.title, err.msg))
        except adm.client.errors.APIError as err:
            error("Internal Server error. Details: {}.".format(err.msg))
        except adm.client.errors.ZdmException as err:
            error("ZDM general error. Details: {}.".format(err.message))
    return wrapper