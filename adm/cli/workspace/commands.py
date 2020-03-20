import click
from base.base import log_table, log_json, error, pass_zcli, info
from base.cfg import env


@click.group()
def workspace():
    """Manage the Workspaces"""
    pass


@workspace.command()
@pass_zcli
def all(zcli):
    """List the  workspace"""
    wks = zcli.adm.workspaces.list()
    if env.human:
        table = []
        for ws in wks:
            table.append(
                [ws.id, ws.name, ws.description, [fleet for fleet in ws.fleets], [device for device in ws.devices]])
        log_table(table, headers=["ID", "Name", "Description" "Fleets", "Devices"])
    else:
        for ws in wks:
            log_json(ws.toJSON())


@workspace.command()
@click.argument('id')
@pass_zcli
def get(zcli, id):
    """Get a workspace"""
    try:
        workspace = zcli.adm.workspaces.get(id)
        # devices = zcli.adm.workspace_get_devices(workspace.Id)
        # log_table([[workspace.Id, workspace.Name, workspace.Description, [fleet.Id for fleet in workspace.Fleets], [device.Id for device in devices]]], headers=["ID", "Name", "Description", "Fleets", "Devices"])
        log_table([[workspace.id, workspace.name, workspace.description]], headers=["ID", "Name", "Description"])

    except Exception as e:
        error(e)


@workspace.command()
@click.argument('name')
@click.option('--description', default="", type=click.STRING, help="Small description af the workspace.")
@pass_zcli
def create(zcli, name, description):
    """Create a workspace"""
    wks = zcli.adm.workspaces.create(name, description)
    log_table([[wks.id, wks.name, wks.description]], headers=["ID", "Name", "Description"])


@workspace.command()
@click.argument('workspace-id')
@pass_zcli
def tags(zcli, workspace_id):
    """Get all the tags of a workspace"""
    tags = zcli.adm.data.list(workspace_id)

    print(tags)
    if len(tags) > 0:
        table = []
        for tag in tags:
            table.append([tag])
        log_table(table, headers=["Name"])
    else:
        info("No tags associated with the workspace ", workspace_id)


@workspace.command()
@click.argument('workspace-id')
@click.argument('tag')
@pass_zcli
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
