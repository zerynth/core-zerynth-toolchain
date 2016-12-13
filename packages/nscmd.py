"""
.. _ztc-cmd-namespace:

**********
Namespaces
**********

Namespaces are attributes of packages used to better organize them. A namespace can be created by a user and packages can be subsequently published under it.
A namespace is owned by a single user that can publish under it. A namespace can be shared with other users to grant them publishing rights.

    """
from base import *
import click


@cli.group(help="Manage namespaces.")
def namespace():
    pass

@namespace.command(help="Create a namespace. \n\n Arguments: \n\n NAME: namespace name.")
@click.argument("name")
def create(name):
    """ 

.. _ztc-cmd-namespace-create:

Create
------

The command: ::

    ztc namespace create name

will create the namespace :samp:`name` and associate it with the user. 
There is a limit on the number of namespaces a user can own and the command fails if the limit is reached.


    """
    info("Creating namespace...")
    try:
        res = zpost(url=env.api.ns, data={"name":name})
        rj = res.json()
        if rj["status"] == "success":
            info("Namespace",name,"created with uid:", rj["data"]["uid"])
        else:
            error("Error in namespace creation:", rj["message"])
    except Exception as e:
        critical("Can't create namespace", exc=e)

@namespace.command()
def share(user):
    """

.. _ztc-cmd-namespace-share:

Share
-----

This feature is not implemented yet.
    """
    fatal("not implemented yet")


@namespace.command("list")
def __list():
    """ 

.. _ztc-cmd-namespace-list:

List
----

The command: ::

    ztc namespace list

retrieves the list of the user namespaces.

    """
    try:
        res = zget(url=env.api.ns)
        rj = res.json()
        if rj["status"]=="success":
            log_json(rj["data"])
        else:
            error("Can't get namespace list",rj["message"])
    except Exception as e:
        critical("Can't create namespace", exc=e)
