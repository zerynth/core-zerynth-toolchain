from base import *
import click
import time
import webbrowser
import json


@cli.command("login")
@click.option("--token",default=None)
def __login(token):
    if not token:
        log("Hello!")
        log("In a few seconds a browser will open to the login page")
        log("Once logged, copy the authorization token and paste it here")
        time.sleep(1)
        webbrowser.open(env.api.sso)
        token = input("Paste the token here and press enter -->")
    if token:
        env.var.set("token",token)
        env.save()
    else:
        error("Bad token!")
