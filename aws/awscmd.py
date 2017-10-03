# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2017-10-03 09:34:26
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-10-03 15:09:23

"""
.. _ztc-cmd-aws:

*******************
Amazon Web Services
*******************

    """

from base import *
import click
from . import awscli
from . import awsthing

@cli.group(help="ztc and AWS IoT integration")
def aws():
    pass


@aws.command("thing_template",help="create a Zerynth project based on a default AWS IoT project template")
@click.argument("project_name")
@click.argument("path",type=click.Path())
@click.option("--aws_endpoint")
@click.option("--aws_policy_name")
def __thing_template(project_name, path, aws_endpoint, aws_policy_name):
    thing_template_path = fs.path(fs.dirname(__file__), 'templates', 'thing_template')
    dst_path = fs.path(path, project_name)
    info("Cloning template")
    fs.copytree(thing_template_path, dst_path) # maybe softer, copytree removes tree!!!
    # TODO: set new project_name to template
    info("Customizing")
    conf_file = fs.path(dst_path, 'thing.conf.json')
    thing_conf = fs.get_json(conf_file)
    thing_conf['endpoint'] = aws_endpoint
    thing_conf['policy_name'] = aws_policy_name
    fs.set_json(thing_conf, conf_file)


@aws.command("to_things",help="create n Zerynth projects each one bound to a newly created thing from a single template project")
@click.argument("base_project_path")
@click.argument("dst_projects_path")
@click.argument("thing_base_name")
@click.option("--things_number", default=1, type=int)
def __to_things(base_project_path, dst_projects_path, thing_base_name, things_number):
    _awscli = awscli.AWSCli()
    for i in range(things_number):
        thingname = thing_base_name + '_' + str(i)
        thing = awsthing.Thing(thingname, _awscli)
        info('Creating thing', thingname)
        thing.create_with_keys_and_certificate()
        thing.to_project(base_project_path, dst_projects_path)