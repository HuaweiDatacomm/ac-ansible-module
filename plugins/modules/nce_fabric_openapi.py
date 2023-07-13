#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
module: nce_fabric_openapi
short_description: Manages Openapi on HUAWEI iMaster NCE-Fabric Controller.
description:
    - Manages Openapi on HUAWEI iMaster NCE-Fabric Controller(AC).
author: ZhiwenZhang (@maomao1995)
notes:
  - This module requires installation iMaster NCE-Fabric Controller.
  - This module also works with C(local) connections for legacy playbooks.
options:
  url:
    description:
    - The url of the openapi.
    type: str
    aliases: [ uri ]
  method:
    description:
    - The url of the openapi.
    type: str
    choices: [ GET, DELETE, POST, PUT ]
  body:
    description:
    - The body of the openapi.
    type: str
    aliases: [ data ]

'''

EXAMPLES = '''

'''

RETURN = ''' 

'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.ac import ACModule, ac_argument_spec, \
    ac_annotation_spec


def main():
    argument_spec = ac_argument_spec()
    argument_spec.update(ac_annotation_spec())
    argument_spec.update(
        url=dict(type="str", required=True, aliases=["uri"]),
        method=dict(type="str", required=True, choices=["GET", "DELETE", "POST", "PUT"]),
        body=dict(type="dict", aliases=["data"]),
        body_json_str=dict(type="str", aliases=["json_str"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    url = module.params.get("url")
    method = module.params.get("method")
    body = module.params.get("body")
    body_json_str = module.params.get("body_json_str")

    ac = ACModule(module)
    ac.operate_config(url, method, body if body else body_json_str)
    ac.exit_json()


if __name__ == '__main__':
    main()
