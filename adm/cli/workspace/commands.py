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
    wks = zcli.adm.workspace_all()
    if env.human:
        table = []
        for ws in wks:
            table.append([ws.Id, ws.Name])
        log_table(table, headers=["ID", "Name"])
    else:
        for ws in wks:
            log_json(ws.toJSON())


@workspace.command()
@click.argument('id')
@pass_zcli
def get(zcli, id):
    """Get a workspace"""
    try:
        workspace = zcli.adm.workspace_get(id)
        log_table([[workspace.Id, workspace.Name, len(workspace.Fleets)]], headers=["ID", "Name", "#fleets"])
    except Exception as e:
        error(e)


@workspace.command()
@click.argument('name')
@click.option('--description', default=1, help="Small description af the workspace.")
@pass_zcli
def create(zcli, name, description):
    """Create a workspace"""
    wks = zcli.adm.workspace_create(name, description)
    log_table([[wks.Id, wks.Name, wks.Description]], headers=["ID", "Name", "Description"])



@workspace.command()
@click.argument('workspace-id')
@pass_zcli
def tags(zcli, workspace_id):
    """Get all the tags of a workspace"""
    tags = zcli.adm.workspace_tags_all(workspace_id)
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


