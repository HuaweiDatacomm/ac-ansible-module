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
module: nce_fabric_logicrouter
short_description: Manages LogicRouter on HUAWEI iMaster NCE-Fabric Controller.
description:
    - Manages LogicRouter on HUAWEI iMaster NCE-Fabric Controller(AC).
author: ZhiwenZhang (@maomao1995)
notes:
  - This module requires installation iMaster NCE-Fabric Controller.
  - This module also works with C(local) connections for legacy playbooks.
options:
  logicrouter:
    description:
    - The name of the LogicRouter.
    type: str
    aliases: [ logicrouter_name ]
  description:
    description:
    - Description for the LogicRouter.
    type: str
    aliases: [ logicrouter_desc ]
  fabric:
    description:
    - The name of the LogicRouter associated master fabric.
    type: str
    aliases: [ fabric_name ]
  logicnetwork:
    description:
    - The name of the LogicRouter associated LogicNetwork.
    type: list
    aliases: [ logicnetwork_name ]    
  operation:
    description:
    - Use C(create) for adding an object.
    - Use C(delete) for removing an object.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ create, delete, query ]
    default: create
'''

EXAMPLES = '''
- name: Add a new logicrouter
  huaweidatacom.nce_fabric.nce_fabric_logicrouter:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicrouter: router1
    description: router1 description
    fabric: fabric1
    logicnetwork: vpc1
    operation: create
  delegate_to: localhost

- name: Delete a old logicrouter
  huaweidatacom.nce_fabric.nce_fabric_logicrouter:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicrouter: router1
    logicnetwork: vpc1
    operation: delete
  delegate_to: localhost
  
- name: Query a logicrouter
  huaweidatacom.nce_fabric.nce_fabric_logicrouter:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicrouter: router1
    logicnetwork: vpc1
    operation: query
  delegate_to: localhost
  register: query_result
  
- name: Query all logicrouters
  huaweidatacom.nce_fabric.nce_fabric_logicrouter:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
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
  sample: https://ip:port/controller/dc/v3/logicnetwork/routers
msg:
  description: The HTTP result info from the API
  returned: result info
  type: str
  sample: {"name": "router1", "description": "Production router1"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.ac import ACModule, ac_argument_spec, \
    ac_annotation_spec
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.utils import get_uuid


def main():
    business = "router"
    argument_spec = ac_argument_spec()
    argument_spec.update(ac_annotation_spec())
    argument_spec.update(
        logicrouter=dict(type="str", aliases=["logicrouter_name"]),
        description=dict(type="str", aliases=["logicrouter_desc"]),
        fabric=dict(type="str", aliases=["fabric_name"]),
        logicnetwork=dict(type="str", aliases=["logicnetwork_name"]),
        operation=dict(type="str", default="create", choices=["create", "delete", "query"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["operation", "create", ["logicrouter", "logicnetwork"]],
            ["operation", "delete", ["logicrouter", "logicnetwork"]],
        ],
    )

    logic_router = module.params.get("logicrouter")
    description = module.params.get("description")
    operation = module.params.get("operation")
    logic_network = module.params.get("logicnetwork")
    fabric = module.params.get("fabric")

    ac = ACModule(module)
    if operation == "create":
        ac.construct_url(business)
        logic_network_id = ac.query_id_by_name("network", logic_network)
        logic_router_id = get_uuid()
        logic_router_info = {
            "id": logic_router_id,
            "name": logic_router,
            "description": description,
            "type": "Normal",
            "logicNetworkId": logic_network_id,
        }
        if fabric:
            logic_router_info["routerLocations"] = [{"fabricRole": "master", "fabricName": fabric}]
        ac.set_config({
            business: logic_router_info
        })
        ac.create_config()
    elif operation == "delete":
        logic_network_id = ac.query_id_by_name("network", logic_network)
        logic_router_id = ac.query_id_by_condition(business, {"name": logic_router, "logicNetworkId": logic_network_id})
        ac.construct_object_url(business, logic_router_id, logic_router)
        ac.delete_config()
    elif operation == "query":
        ac.construct_url(business)
        if logic_router and logic_network:
            logic_network_id = ac.query_id_by_name("network", logic_network)
            ac.query_config(business, {"name": logic_router, "logicNetworkId": logic_network_id})
        elif logic_router:
            ac.query_config(business, {"name": logic_router})
        else:
            ac.query_config(business)
    ac.exit_json()


if __name__ == '__main__':
    main()
