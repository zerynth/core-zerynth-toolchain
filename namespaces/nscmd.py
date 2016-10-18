from base import *
import click
import datetime
import json
import sys

ns_url = "http://localhost/zbackend/namespaces/"

@cli.group()
def namespace():
    pass

@namespace.command()
@click.argument("name")
def create(name):
    nsinfo = {
        "name":name,
        }
    info("Creating requested namespace...")
    headers = {"Authorization": "Bearer "+env.token}
    try:
        res = zpost(url=ns_url, headers=headers, data=nsinfo)
        if res.json()["status"] == "success":
            nsinfo.update({"uid": res.json()["data"]["uid"]})
            info("Namespace",name,"created with uid:", res.json()["data"]["uid"])
        else:
            error("Error in creating namespace:", res.json()["message"])
    except Exception as e:
        fatal("Can't create namespace", e)