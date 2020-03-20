import click
from base.base import log_table, log_json, pass_zcli, info
from base.cfg import env

from ..helper import handle_error


@click.group()
def workspace():
    """Manage the Workspaces"""
    pass


@workspace.command()
@pass_zcli
@handle_error
def all(zcli):
    """List all the workspace"""
    wks = zcli.adm.workspaces.list()
    if env.human:
        table = []
        for ws in wks:
            table.append([ws.id, ws.name, ws.description, ws.fleets, ws.devices])
        log_table(table, headers=["ID", "Name", "Description" "Fleets", "Devices"])
    else:
        for ws in wks:
            log_json(ws.toJSON())


@workspace.command()
@click.argument('id')
@pass_zcli
@handle_error
def get(zcli, id):
    """Get a workspace"""
    ws = zcli.adm.workspaces.get(id)
    data = [ws.id, ws.name, ws.description, ws.fleets, ws.devices]
    log_table([data], headers=["ID", "Name", "Description", "Fleets", "Devices"])


@workspace.command()
@click.argument('name')
@click.option('--description', default="", type=click.STRING, help="Small description af the workspace.")
@pass_zcli
@handle_error
def create(zcli, name, description):
    """Create a workspace"""
    wks = zcli.adm.workspaces.create(name, description)
    log_table([[wks.id, wks.name, wks.description]], headers=["ID", "Name", "Description"])


@workspace.command()
@click.argument('workspace-id')
@pass_zcli
@handle_error
def tags(zcli, workspace_id):
    """Get all the tags of a workspace"""
    tags = zcli.adm.data.list(workspace_id)
    if len(tags) > 0:
        log_table([[tags]], headers=["Tags"])
    else:
        info("No tags associated with the workspace ", workspace_id)


@workspace.command()
@click.argument('workspace-id')
@click.argument('tag')
@pass_zcli
@handle_error
def data(zcli, workspace_id, tag):
    """Get all the data of a workspace associated to a tag"""
    tags = zcli.adm.workspace_data_get(workspace_id, tag)
    if len(tags) > 0:
        table = []
        for tag in tags:
            table.append([tag.Tag, tag.Payload, tag.DeviceId, tag.Timestamp])
        log_table(table, headers=["Tag", "Payload", "Device", "Timestamp"])
    else:
        info("No data for ", tag, " in workspace ", workspace_id)
