# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2017-10-03 10:34:40
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-10-03 14:49:49

from base import *

class AWSCli:

    def __init__(self):
        pass

    def create_thing(self, thingname):
        code, out, _ = proc.run('aws','iot','create-thing','--thing-name', thingname)

    def create_keys_and_certificate(self):
        code, out, _ = proc.run('aws','iot','create-keys-and-certificate','--set-as-active')
        return json.loads(out)

    def attach_thing_principal(self, thingname, principal_arn):
        code, out, _ = proc.run('aws','iot','attach-thing-principal','--thing-name', thingname, 
                        '--principal', principal_arn)

    def attach_principal_policy(self, principal_arn, policy_name):
        code, out, err = proc.run('aws','iot','attach-principal-policy','--principal', principal_arn, 
                        '--policy-name', policy_name)
