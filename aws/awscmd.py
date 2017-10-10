# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2017-10-03 09:34:26
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-10-10 17:09:09

"""
.. _ztc-cmd-aws:

*******************
Amazon Web Services
*******************

The integration between the Zerynth Toolchain and AWS command line tool allows to easily manage AWS resources 

The following commands are available: 

    * AWS IoT Platform:

        * :ref:`thing-project-from-template <ztc-cmd-aws-thing_project_from_template>`
        * :ref:`set-active-thing <ztc-cmd-aws-set_active_thing>`
        * :ref:`add-things <ztc-cmd-aws-add_things>`
        * :ref:`__clean <ztc-cmd-aws-__clean>`

    """

from base import *
import click
from . import awscli
from . import awsthing

zawsconf_filename = '.zawsconf'
thingsresources_dirname = '.aws_things_resources'

@cli.group(help="ztc and AWS cli integration")
def aws():
    pass


"""
================
AWS IoT Platform
================
"""

@aws.command("thing-project-from-template",help="create a Zerynth project based on a default AWS IoT project template")
@click.argument("project-name")
@click.argument("path",type=click.Path())
@click.option("--aws-endpoint")
@click.option("--aws-policy-name")
def __thing_template(project_name, path, aws_endpoint, aws_policy_name):
    """ 

.. _ztc-cmd-aws-thing_project_from_template:

Create a generic AWS IoT Thing project from template
----------------------------------------------------

The command: ::

    ztc thing-project-from-template project-name path


    """
    thing_template_path = fs.path(fs.dirname(__file__), 'templates', 'thing_template')
    dst_path = fs.path(path, project_name)
    info("Cloning template")
    fs.copytree(thing_template_path, dst_path) # maybe softer, copytree removes tree!!!
    pinfo = {
        "title": project_name,
        "created_at":str(datetime.datetime.utcnow()),
        "description":"AWS IoT Thing Template"
    }
    res = zpost(url=env.api.project, data=pinfo)
    rj = res.json()
    if rj["status"] == "success":
        pinfo.update({"uid": rj["data"]["uid"]})
    fs.set_json(pinfo, fs.path(dst_path,".zproject"))

    info("Customizing")
    conf_file = fs.path(dst_path, awsthing.thing_conf_filename)
    thing_conf = fs.get_json(conf_file)
    thing_conf['endpoint'] = aws_endpoint
    thing_conf['policy_name'] = aws_policy_name
    fs.set_json(thing_conf, conf_file)

@aws.command("set-active-thing",help="set active thing for Zerynth project compilation")
@click.argument("project-path", type=click.Path())
@click.option("--thing-id", default=0, type=int)
def __set_active_thing(project_path, thing_id):
    zawsconf_file = fs.path(project_path, zawsconf_filename)
    if not fs.isfile(zawsconf_file):
        fatal('cannot set active Thing for a Zerynth project with no things bound to it')

    thingsresources_dir = fs.path(project_path, thingsresources_dirname)
    if not fs.isdir(thingsresources_dir):
        fatal(thingsresources_dir, ' should be a folder!')

    zawsconf = fs.get_json(zawsconf_file)
    thingname = zawsconf['thing_base_name'] + '_' + str(thing_id)
    thing_resources = fs.path(thingsresources_dir, thingname)
    if not fs.isdir(thing_resources):
        fatal(thing_resources, 'should be a folder!')

    awsthing.Thing.set_active(project_path, zawsconf['thing_base_name'], thing_id)
    info(thingname, 'set as active thing')


@aws.command("add-things",help="create n new things bounded to chosen Zerynth Project")
@click.argument("project-path", type=click.Path())
@click.option("--thing-base-name", default='', type=str)
@click.option("--things-number", default=1, type=int)
def __add_things(project_path, thing_base_name, things_number):
    _awscli = awscli.AWSCli()
    zawsconf_file = fs.path(project_path, zawsconf_filename)
    zawsconf = {}
    zawsconf['last_thing_id'] = -1
    if fs.isfile(zawsconf_file):
        zawsconf = fs.get_json(zawsconf_file)
        thing_base_name = zawsconf['thing_base_name']

    if thing_base_name == '':
        fatal('--thing-base-name option mandatory for a Zerynth project with no things already bound to it')

    thingsresources_dir = fs.path(project_path, thingsresources_dirname)
    if not fs.exists(thingsresources_dir):
        fs.makedirs(thingsresources_dir)

    if not fs.isdir(thingsresources_dir):
        fatal(thingsresources_dir, 'should be a folder!')

    tconf_file = fs.path(project_path, awsthing.thing_conf_filename)
    if not fs.isfile(tconf_file):
        fatal('thing conf file missing!')
    tconf = fs.get_json(tconf_file)

    for i in range(zawsconf['last_thing_id']+1, zawsconf['last_thing_id']+1 + things_number):
        thingname = thing_base_name + '_' + str(i)
        thing = awsthing.Thing(thingname, _awscli, fs.path(thingsresources_dir, thingname))
        info('Creating thing', thingname)
        thing.create_with_keys_and_certificate()
        thing.set_policy(tconf['policy_name'])
        thing.store()

    zawsconf['thing_base_name'] = thing_base_name
    zawsconf['last_thing_id'] += (things_number)
    fs.set_json(zawsconf, zawsconf_file)

    if not 'active_thing_id' in zawsconf:
        awsthing.Thing.set_active(project_path, thing_base_name, 0)


@aws.command("__clean",help="destroy things and certificates (both local and remote)")
@click.argument("project-path", type=click.Path())
def __clean(project_path):
    _awscli = awscli.AWSCli()

    thingsresources_dir = fs.path(project_path, thingsresources_dirname)

    for thing_path in fs.glob(thingsresources_dir, '*'):
        thingname = fs.split(thing_path)[-1]
        info('deleting ', thingname)
        thing = awsthing.Thing(thingname, _awscli, fs.path(thingsresources_dir, thingname))
        thing.delete()

    fs.rmtree(thingsresources_dir)
    fs.rm_file(fs.path(project_path, zawsconf_filename))
