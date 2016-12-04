from base import *
import click


@cli.group()
def namespace():
    pass

@namespace.command("list")
def __list():
    try:
        res = zget(url=env.api.ns)
        rj = res.json()
        if rj["status"]=="success":
            log_json(rj["data"])
        else:
            error("Can't get namespace list",rj["message"])
    except Exception as e:
        critical("Can't create namespace", exc=e)


@namespace.command()
@click.argument("name")
def create(name):
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