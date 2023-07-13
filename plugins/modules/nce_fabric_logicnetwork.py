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
module: nce_fabric_logicnetwork
short_description: Manages LogicNetwork on HUAWEI iMaster NCE-Fabric Controller.
description:
    - Manages LogicNetwork on HUAWEI iMaster NCE-Fabric Controller(AC).
author: ZhiwenZhang (@maomao1995)
notes:
  - This module requires installation iMaster NCE-Fabric Controller.
  - This module also works with C(local) connections for legacy playbooks.
options:
  logicnetwork:
    description:
    - The name of the LogicNetwork.
    type: str
    aliases: [ logicnetwork_name ]
  description:
    description:
    - Description for the LogicNetwork.
    type: str
    aliases: [ logicnetwork_desc ]    
  fabrics:
    description:
    - The name of the LogicNetwork associated fabrics.
    type: list
    aliases: [ fabric_names ]
  tenant:
    description:
    - The name of the LogicNetwork associated tenant.
    type: str
    aliases: [ tenant_name ]    
'''

EXAMPLES = '''
- name: Add a new logicnetwork
  huaweidatacom.nce_fabric.nce_fabric_logicnetwork:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicnetwork: vpc1
    description: vpc1 description
    fabrics: [fabric1]
    tenant: tenant1
    operation: create
  delegate_to: localhost

- name: Update a old logicnetwork
  huaweidatacom.nce_fabric.nce_fabric_logicnetwork:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicnetwork: vpc1
    description: vpc1 description update
    fabrics: [fabric1]
    tenant: tenant1
    operation: update
  delegate_to: localhost

- name: Delete a old logicnetwork
  huaweidatacom.nce_fabric.nce_fabric_logicnetwork:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicnetwork: vpc1
    operation: delete
  delegate_to: localhost

- name: Query all logicnetworks
  huaweidatacom.nce_fabric.nce_fabric_logicnetwork:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    operation: query
  delegate_to: localhost
  register: query_result

- name: Query a logicnetwork
  huaweidatacom.nce_fabric.nce_fabric_logicnetwork:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicnetwork: vpc1
    operation: query
  delegate_to: localhost
  register: query_result
'''

RETURN = ''' 
method:
  description: The HTTP method used for the request to the API
  returned: failure or debug
  type: str
  sample: POST
response:
  description: The HTTP response from the API
  returned: failure or debug
  type: str
  sample: OK (30 bytes)
status:
  description: The HTTP status from the API
  returned: failure or debug
  type: int
  sample: 200
url:
  description: The HTTP url used for the request to the API
  returned: failure or debug
  type: str
  sample: https://ip:port/controller/dc/v3/logicnetwork/networks
msg:
  description: The HTTP result info from the API
  returned: result info
  type: str
  sample: {"name": "vpc1", "description": "Production vpc1"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.ac import ACModule, ac_argument_spec, \
    ac_annotation_spec
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.utils import get_uuid


def main():
    business = "network"
    argument_spec = ac_argument_spec()
    argument_spec.update(ac_annotation_spec())
    argument_spec.update(
        logicnetwork=dict(type="str", aliases=["logicnetwork_name"]),
        description=dict(type="str", aliases=["logicnetwork_desc"]),
        fabrics=dict(type="list", aliases=["fabric_names"]),
        tenant=dict(type="str", aliases=["tenant_name"]),
        operation=dict(type="str", default="create", choices=["create", "delete", "update", "query"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["operation", "create", ["logicnetwork", "fabrics", "tenant"]],
            ["operation", "delete", ["logicnetwork"]],
            ["operation", "update", ["logicnetwork"]],
        ],
    )

    logic_network = module.params.get("logicnetwork")
    description = module.params.get("description")
    operation = module.params.get("operation")
    tenant = module.params.get("tenant")
    fabrics = module.params.get("fabrics")

    ac = ACModule(module)
    if operation == "create":
        fabric_ids = [ac.query_id_by_name("fabric", fabric) for fabric in fabrics]
        tenant_id = ac.query_id_by_name("tenant", tenant)
        logic_network_id = get_uuid()
        ac.construct_url(business)
        ac.set_config({
            business: {
                "id": logic_network_id,
                "name": logic_network,
                "description": description,
                "tenantId": tenant_id,
                "fabricId": fabric_ids
            }
        })
        ac.create_config()
    elif operation == "update":
        tenant_id = ac.query_id_by_name("tenant", tenant)
        logic_network_id = ac.query_id_by_name(business, logic_network)
        ac.construct_object_url(business, logic_network_id, logic_network)
        logic_network_info = {
            "id": logic_network_id,
            "name": logic_network,
            "description": description,
            "tenantId": tenant_id,
        }
        if fabrics:
            fabric_ids = [ac.query_id_by_name("fabric", fabric) for fabric in fabrics]
            logic_network_info["fabricId"] = fabric_ids
        ac.set_config({
            business: logic_network_info
        })
        ac.update_config()
    elif operation == "delete":
        logic_network_id = ac.query_id_by_name(business, logic_network)
        ac.construct_object_url(business, logic_network_id, logic_network)
        ac.delete_config()
    elif operation == "query":
        ac.construct_url(business)
        if logic_network:
            ac.query_config(business, {"name": logic_network})
        else:
            ac.query_config(business)
    ac.exit_json()


if __name__ == '__main__':
    main()
