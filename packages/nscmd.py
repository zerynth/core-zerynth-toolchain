from base import *
import click


@cli.group()
def namespace():
    pass

@namespace.command("list")
@click.option("--pretty","pretty",flag_value=True, default=False,help="output info in readable format")
def __list(pretty):
    indent = 4 if pretty else None
    try:
        res = zget(url=env.api.ns)
        rj = res.json()
        if rj["status"]=="success":
            log(json.dumps(rj["data"],indent=indent))
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