# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2017-10-03 12:34:29
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-10-03 14:51:42

from base import *

class Thing:

    def __init__(self, thingname, awscli):
        self.thingname = thingname
        self._awscli = awscli

    def create_with_keys_and_certificate(self):
        self._awscli.create_thing(self.thingname)

        data = self._awscli.create_keys_and_certificate()
        self.cert_arn = data['certificateArn']
        self.certificate = data['certificatePem']
        self.private_key = data['keyPair']['PrivateKey']

        self._awscli.attach_thing_principal(self.thingname, self.cert_arn)
        info(self.thingname, 'created and certificate attached')

    def to_project(self, base_project_path, dst_project_path):
        project_path = fs.path(dst_project_path, self.thingname)
        fs.copytree(base_project_path, project_path)
        conf_file = fs.path(project_path, 'thing.conf.json')
        thing_conf = fs.get_json(conf_file)
        thing_conf['mqttid'] = self.thingname
        thing_conf['thingname'] = self.thingname
        thing_conf['cert_arn'] = self.cert_arn
        self.policy_name = thing_conf['policy_name']
        fs.set_json(thing_conf, conf_file)

        # policy is attached here
        self._awscli.attach_principal_policy(self.cert_arn, self.policy_name)

        with open(fs.path(project_path, 'certificate.pem.crt'), 'w+') as ww:
            ww.write(self.certificate)
        with open(fs.path(project_path, 'private.pem.key'), 'w+') as ww:
            ww.write(self.private_key)

        info(self.thingname, 'project ready')