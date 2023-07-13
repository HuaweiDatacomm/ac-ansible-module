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
module: nce_fabric_logicsubnet
short_description: Manages LogicSubnet on HUAWEI iMaster NCE-Fabric Controller.
description:
    - Manages LogicSubnet on HUAWEI iMaster NCE-Fabric Controller(AC).
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
  logicnetwork:
    description:
    - The name of the LogicRouter associated LogicNetwork.
    type: list
    aliases: [ logicnetwork_name ]
  cidr:
    description:
    - The cidr of the LogicRouter associated LogicSubnet.
    type: str
    aliases: [ logicsubnet_cidr ]
  gateway_ip:
    description:
    - The gateway ip of the LogicRouter associated LogicSubnet.
    type: str
    aliases: [ logicsubnet_gateway_ip ]
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
- name: Add a new logicsubnet
  huaweidatacom.nce_fabric.nce_fabric_logicsubnet:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicrouter: router1
    cidr: 1.1.1.0/24
    gateway_ip: 1.1.1.1
    logicnetwork: vpc1
    operation: create
  delegate_to: localhost

- name: Delete a old logicsubnet
  huaweidatacom.nce_fabric.nce_fabric_logicsubnet:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicrouter: router1
    logicnetwork: vpc1
    cidr: 1.1.1.0/24
    operation: delete
  delegate_to: localhost
  
- name: Query a logicsubnet
  huaweidatacom.nce_fabric.nce_fabric_logicsubnet:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicrouter: router1
    logicnetwork: vpc1
    operation: query
  delegate_to: localhost
  register: query_result
- debug: var=query_result

- name: Query all logicsubnets
  huaweidatacom.nce_fabric.nce_fabric_logicsubnet:
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
  sample: https://ip:port/controller/dc/v3/logicnetwork/subnets
msg:
  description: The HTTP result info from the API
  returned: result info
  type: str
  sample: {"cidr": "1.1.1.0/24", "gatewayIp": "1.1.1.1"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.ac import ACModule, ac_argument_spec, \
    ac_annotation_spec
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.utils import get_uuid


def main():
    business = "subnet"
    argument_spec = ac_argument_spec()
    argument_spec.update(ac_annotation_spec())
    argument_spec.update(
        logicrouter=dict(type="str", aliases=["logicrouter_name"]),
        cidr=dict(type="str", aliases=["logicsubnet_cidr"]),
        gateway_ip=dict(type="str", aliases=["logicsubnet_gateway_ip"]),
        logicnetwork=dict(type="str", aliases=["logicnetwork_name"]),
        operation=dict(type="str", default="create", choices=["create", "delete", "query"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["operation", "create", ["logicrouter", "logicnetwork", "cidr", "gateway_ip"]],
            ["operation", "delete", ["logicrouter", "logicnetwork", "cidr"]],
        ],
    )

    logic_router = module.params.get("logicrouter")
    cidr = module.params.get("cidr")
    operation = module.params.get("operation")
    logic_network = module.params.get("logicnetwork")
    gateway_ip = module.params.get("gateway_ip")

    ac = ACModule(module)
    if operation == "create":
        ac.construct_url(business)
        logic_network_id = ac.query_id_by_name("network", logic_network)
        logic_router_id = ac.query_id_by_condition("router", {"name": logic_router, "logicNetworkId": logic_network_id})
        logic_subnet_id = get_uuid()
        ac.set_config({
            business: [{
                "id": logic_subnet_id,
                "cidr": cidr,
                "gatewayIp": gateway_ip,
                "logicRouterId": logic_router_id,
            }]
        })
        ac.create_config()
    elif operation == "delete":
        logic_network_id = ac.query_id_by_name("network", logic_network)
        logic_router_id = ac.query_id_by_condition("router", {"name": logic_router, "logicNetworkId": logic_network_id})
        logic_subnet_id = ac.query_id_by_condition(business, {"cidr": cidr, "logicRouterId": logic_router_id})
        ac.construct_object_url(business, logic_subnet_id, cidr)
        ac.delete_config()
    elif operation == "query":
        ac.construct_url(business)
        if logic_router and logic_network:
            logic_network_id = ac.query_id_by_name("network", logic_network)
            logic_router_id = ac.query_id_by_condition("router",
                                                       {"name": logic_router, "logicNetworkId": logic_network_id})
            ac.query_config(business, {"logicRouterId": logic_router_id})
        else:
            ac.query_config(business)
    ac.exit_json()


if __name__ == '__main__':
    main()
