import click

from adm.client.admclient import ADMClient

pass_adm = click.make_pass_decorator(ADMClient, ensure=True)
