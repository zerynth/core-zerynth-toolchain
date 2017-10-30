# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2017-10-03 10:34:40
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-10-10 15:53:40

from base import *

class AWSCli:

    def __init__(self):
        pass

    def create_thing(self, thingname):
        code, out, _ = proc.run('aws','iot','create-thing','--thing-name', thingname)

    def delete_thing(self, thingname):
        code, out, _ = proc.run('aws','iot','delete-thing','--thing-name', thingname)

    def create_keys_and_certificate(self):
        code, out, _ = proc.run('aws','iot','create-keys-and-certificate','--set-as-active')
        return json.loads(out)

    def attach_thing_principal(self, thingname, principal_arn):
        code, out, _ = proc.run('aws','iot','attach-thing-principal','--thing-name', thingname, 
                        '--principal', principal_arn)

    def detach_thing_principal(self, thingname, principal_arn):
        code, out, _ = proc.run('aws','iot','detach-thing-principal','--thing-name', thingname, 
                        '--principal', principal_arn)

    def get_thing_principals(self, thingname):
        code, out, _ = proc.run('aws','iot','list-thing-principals','--thing-name', thingname)
        return json.loads(out)

    def attach_principal_policy(self, principal_arn, policy_name):
        code, out, err = proc.run('aws','iot','attach-principal-policy','--principal', principal_arn, 
                        '--policy-name', policy_name)

    def detach_principal_policy(self, principal_arn, policy_name):
        code, out, err = proc.run('aws','iot','detach-principal-policy','--principal', principal_arn, 
                        '--policy-name', policy_name)

    def get_principal_policies(self, principal_arn):
        code, out, err = proc.run('aws','iot','list-principal-policies','--principal', principal_arn)
        return json.loads(out)

    def delete_certificate(self, certificate_id):
        code, out, _ = proc.run('aws','iot','update-certificate','--certificate-id', certificate_id, 
                        '--new-status', 'INACTIVE')
        code, out, _ = proc.run('aws','iot','delete-certificate','--certificate-id', certificate_id)

