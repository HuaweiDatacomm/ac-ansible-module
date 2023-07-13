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
module: nce_fabric_logicinterface
short_description: Manages LogicInterface on HUAWEI iMaster NCE-Fabric Controller.
description:
    - Manages LogicInterface on HUAWEI iMaster NCE-Fabric Controller(AC).
author: ZhiwenZhang (@maomao1995)
notes:
  - This module requires installation iMaster NCE-Fabric Controller.
  - This module also works with C(local) connections for legacy playbooks.
options:
  logicinterface:
    description:
    - The name of the LogicInterface.
    type: str
    aliases: [ logicinterface_name ]
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
  logicswitch:
    description:
    - The name of the LogicSwitch.
    type: str
    aliases: [ logicswitch_name ]
  cidrs:
    description:
    - The cidrs of the LogicRouter associated LogicSubnet.
    type: list
    aliases: [ logicsubnet_cidrs ]
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
- name: Add a new logicinterface
  huaweidatacom.nce_fabric.nce_fabric_logicinterface:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicinterface: interface1
    logicrouter: router1
    cidrs: [1.1.1.0/24]
    logicswitch: switch1
    logicnetwork: vpc1
    operation: create
  delegate_to: localhost

- name: Delete a old logicinterface
  huaweidatacom.nce_fabric.nce_fabric_logicinterface:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicinterface: interface1
    logicrouter: router1
    logicnetwork: vpc1
    operation: delete
  delegate_to: localhost
  
- name: Query a logicinterface
  huaweidatacom.nce_fabric.nce_fabric_logicinterface:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    logicinterface: interface1
    operation: query
  delegate_to: localhost
  register: query_result

- name: Query all logicinterfaces
  huaweidatacom.nce_fabric.nce_fabric_logicinterface:
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
  sample: https://ip:port/controller/dc/v3/logicnetwork/interfaces
msg:
  description: The HTTP result info from the API
  returned: result info
  type: str
  sample: {"name": "interface1", "description": "Production interface1"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.ac import ACModule, ac_argument_spec, \
    ac_annotation_spec
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.utils import get_uuid

def main():
    business = "interface"
    argument_spec = ac_argument_spec()
    argument_spec.update(ac_annotation_spec())
    argument_spec.update(
        logicinterface=dict(type="str", aliases=["logicinterface_name"]),
        logicrouter=dict(type="str", aliases=["logicrouter_name"]),
        cidrs=dict(type="list", aliases=["logicsubnet_cidrs"]),
        logicswitch=dict(type="str", aliases=["logicswitch_name"]),
        logicnetwork=dict(type="str", aliases=["logicnetwork_name"]),
        operation=dict(type="str", default="create", choices=["create", "delete", "query"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["operation", "create", ["logicinterface", "logicrouter", "logicnetwork", "cidrs", "logicswitch"]],
            ["operation", "delete", ["logicinterface", "logicrouter", "logicnetwork"]],
        ],
    )

    logic_interface = module.params.get("logicinterface")
    logic_router = module.params.get("logicrouter")
    cidrs = module.params.get("cidrs")
    operation = module.params.get("operation")
    logic_network = module.params.get("logicnetwork")
    logic_switch = module.params.get("logicswitch")

    ac = ACModule(module)
    if operation == "create":
        ac.construct_url(business)
        logic_network_id = ac.query_id_by_name("network", logic_network)
        logic_router_id = ac.query_id_by_condition("router", {"name": logic_router, "logicNetworkId": logic_network_id})
        logic_switch_id = ac.query_id_by_condition("switch", {"name": logic_switch, "logicNetworkId": logic_network_id})
        logic_subnet_ids = [ac.query_id_by_condition("subnet", {"cidr": cidr, "logicRouterId": logic_router_id}) for
                            cidr in cidrs]
        logic_interface_id = get_uuid()
        ac.set_config({
            business: [{
                "id": logic_interface_id,
                "name": logic_interface,
                "interfaceType": "RouterInterface",
                "logicRouterId": logic_router_id,
                "logicSwitchId": logic_switch_id,
                "ip": {
                    "subnetIds": logic_subnet_ids,
                }
            }]
        })
        ac.create_config()
    elif operation == "delete":
        logic_network_id = ac.query_id_by_name("network", logic_network)
        logic_router_id = ac.query_id_by_condition("router", {"name": logic_router, "logicNetworkId": logic_network_id})
        logic_interface_id = ac.query_id_by_condition(business,
                                                      {"name": logic_interface, "logicRouterId": logic_router_id})
        ac.construct_object_url(business, logic_interface_id, logic_interface)
        ac.delete_config()
    elif operation == "query":
        ac.construct_url(business)
        if logic_router and logic_network and logic_interface:
            logic_network_id = ac.query_id_by_name("network", logic_network)
            logic_router_id = ac.query_id_by_condition("router",
                                                       {"name": logic_router, "logicNetworkId": logic_network_id})
            ac.query_config(business, {"name": logic_interface, "logicRouterId": logic_router_id})
        elif logic_interface:
            ac.query_config(business, {"name": logic_interface})
        else:
            ac.query_config(business)
    ac.exit_json()


if __name__ == '__main__':
    main()
