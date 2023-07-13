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
module: nce_fabric_endport
short_description: Manages EndPort on HUAWEI iMaster NCE-Fabric Controller.
description:
    - Manages EndPort on HUAWEI iMaster NCE-Fabric Controller(AC).
author: ZhiwenZhang (@maomao1995)
notes:
  - This module requires installation iMaster NCE-Fabric Controller.
  - This module also works with C(local) connections for legacy playbooks.
options:
  endport:
    description:
    - The name of the EndPort.
    type: str
    aliases: [ endport_name ]
  description:
    description:
    - Description for the EndPort.
    type: str
    aliases: [ endport_desc ]
  logicport:
    description:
    - The name of the LogicPort.
    type: str
    aliases: [ logicport_name ]
  logicnetwork:
    description:
    - The name of the LogicPort associated LogicNetwork.
    type: list
    aliases: [ logicnetwork_name ]
  logicswitch:
    description:
    - The name of the LogicSwitch.
    type: str
    aliases: [ logicswitch_name ]
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
- name: Add a new endport
  huaweidatacom.nce_fabric.nce_fabric_endport:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    endport: endport1
    description: description endport1
    logicport: port1
    logicswitch: switch1
    logicnetwork: vpc1
    operation: create
  delegate_to: localhost

- name: Delete a old endport
  huaweidatacom.nce_fabric.nce_fabric_endport:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    endport: endport1
    logicnetwork: vpc1
    operation: delete
  delegate_to: localhost
  
- name: Query a endport
  huaweidatacom.nce_fabric.nce_fabric_endport:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    endport: endport1
    operation: query
  delegate_to: localhost
  register: query_result

- name: Query all endports
  huaweidatacom.nce_fabric.nce_fabric_endport:
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
  sample: https://ip:port/controller/dc/v3/logicnetwork/endports
msg:
  description: The HTTP result info from the API
  returned: result info
  type: str
  sample: {"name": "endport1", "description": "Production endport1"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.ac import ACModule, ac_argument_spec, \
    ac_annotation_spec
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.utils import get_uuid


def main():
    business = "endPort"
    business_query = "endPorts"
    argument_spec = ac_argument_spec()
    argument_spec.update(ac_annotation_spec())
    argument_spec.update(
        endport=dict(type="str", aliases=["endport_name"]),
        description=dict(type="str", aliases=["endport_desc"]),
        logicport=dict(type="str", aliases=["logicport_name"]),
        logicnetwork=dict(type="str", aliases=["logicnetwork_name"]),
        logicswitch=dict(type="str", aliases=["logicswitch_name"]),
        operation=dict(type="str", default="create", choices=["create", "delete", "query"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["operation", "create", ["endport", "logicport", "logicswitch", "logicnetwork"]],
            ["operation", "delete", ["endport", "logicnetwork"]],
        ],
    )

    end_port = module.params.get("endport")
    logic_port = module.params.get("logicport")
    description = module.params.get("description")
    operation = module.params.get("operation")
    logic_network = module.params.get("logicnetwork")
    logic_switch = module.params.get("logicswitch")

    ac = ACModule(module)
    if operation == "create":
        ac.construct_url(business)
        logic_network_id = ac.query_id_by_name("network", logic_network)
        logic_switch_id = ac.query_id_by_condition("switch", {"name": logic_switch, "logicNetworkId": logic_network_id})
        logic_port_id = ac.query_id_by_condition("port", {"name": logic_port, "logicSwitchId": logic_switch_id})
        end_port_id = get_uuid()
        ac.set_config({
            business: {
                "id": end_port_id,
                "name": end_port,
                "description": description,
                "logicNetworkId": logic_network_id,
                "logicPortId": logic_port_id,
            }
        })
        ac.create_config()
    elif operation == "delete":
        logic_network_id = ac.query_id_by_name("network", logic_network)
        end_port_id = ac.query_id_by_condition(business_query, {"name": end_port, "logicNetworkId": logic_network_id})
        ac.construct_object_url(business, end_port_id, end_port)
        ac.delete_config()
    elif operation == "query":
        ac.construct_url(business)
        if end_port and logic_network:
            logic_network_id = ac.query_id_by_name("network", logic_network)
            ac.query_config(business_query, {"name": end_port, "logicNetworkId": logic_network_id})
        elif end_port:
            ac.query_config(business_query, {"name": end_port})
        else:
            ac.query_config(business_query)
    ac.exit_json()


if __name__ == '__main__':
    main()
