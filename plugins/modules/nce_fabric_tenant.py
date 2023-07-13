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
module: nce_fabric_tenant
short_description: Manages Tenant on HUAWEI iMaster NCE-Fabric Controller.
description:
    - Manages Tenant on HUAWEI iMaster NCE-Fabric Controller(AC).
author: ZhiwenZhang (@maomao1995)
notes:
  - This module requires installation iMaster NCE-Fabric Controller.
  - This module also works with C(local) connections for legacy playbooks.
options:
  tenant:
    description:
    - The name of the tenant.
    type: str
    aliases: [ tenant_name ]
  description:
    description:
    - Description for the tenant.
    type: str
    aliases: [ tenant_desc ]
  fabrics:
    description:
    - The name of the tenant associated fabrics.
    type: list
    aliases: [ fabric_names ]
  operation:
    description:
    - Use C(create) for adding an object.
    - Use C(update) for update an object.
    - Use C(delete) for removing an object.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ create, delete, update, query ]
    default: create
'''

EXAMPLES = '''
- name: Create a new tenant
  huaweidatacom.nce_fabric.nce_fabric_tenant:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    tenant: tenant_test
    description: tenant tenant_test
    fabrics: [fabric_test]
    operation: create
  delegate_to: localhost
  
- name: Update a old tenant
  huaweidatacom.nce_fabric.nce_fabric_tenant:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    tenant: tenant_test
    description: tenant tenant_test
    fabrics: [fabric_test]
    operation: update
  delegate_to: localhost

- name: Delete a old tenant
  huaweidatacom.nce_fabric.nce_fabric_tenant:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    tenant: tenant_test
    description: tenant tenant_test
    operation: delete
  delegate_to: localhost
  
- name: Query a tenant
  huaweidatacom.nce_fabric.nce_fabric_tenant:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    tenant: tenant_test
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all tenants
  huaweidatacom.nce_fabric.nce_fabric_tenant:
    host: host1
    port: 18002
    username: admin
    password: SomeSecretPassword
    state: query
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
  sample: https://ip:port/controller/dc/v3/tenants
msg:
  description: The HTTP result info from the API
  returned: result info
  type: str
  sample: {"name": "tenant1", "description": "Production tenant1"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.ac import ACModule, ac_argument_spec, \
    ac_annotation_spec
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.utils import get_uuid


def main():
    business = "tenant"
    argument_spec = ac_argument_spec()
    argument_spec.update(ac_annotation_spec())
    argument_spec.update(
        tenant=dict(type="str", aliases=["tenant_name"]),
        description=dict(type="str", aliases=["tenant_desc"]),
        fabrics=dict(type="list", aliases=["fabric_names"]),
        operation=dict(type="str", default="create", choices=["create", "delete", "update", "query"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["operation", "create", ["tenant", "fabrics"]],
            ["operation", "delete", ["tenant"]],
            ["operation", "update", ["tenant"]],
        ],
    )

    description = module.params.get("description")
    operation = module.params.get("operation")
    tenant = module.params.get("tenant")
    fabrics = module.params.get("fabrics")

    ac = ACModule(module)
    if operation == "create":
        fabric_ids = [ac.query_id_by_name("fabric", fabric) for fabric in fabrics]
        tenant_id = get_uuid()
        ac.construct_url(business)
        ac.set_config({
            business: [{
                "id": tenant_id,
                "name": tenant,
                "description": description,
                "resPool": {
                    "fabricIds": fabric_ids
                }
            }]
        })
        ac.create_config()
    elif operation == "update":
        tenant_id = ac.query_id_by_name(business, tenant)
        ac.construct_object_url(business, tenant_id, tenant)
        tenant_info = {
            "id": tenant_id,
            "name": tenant,
            "description": description,
        }
        if fabrics:
            fabric_ids = [ac.query_id_by_name("fabric", fabric) for fabric in fabrics]
            tenant_info["resPool"] = {"fabricIds": fabric_ids}
        ac.set_config({
            business: [tenant_info]
        })
        ac.update_config()
    elif operation == "delete":
        tenant_id = ac.query_id_by_name(business, tenant)
        ac.construct_object_url(business, tenant_id, tenant)
        ac.delete_config()
    elif operation == "query":
        ac.construct_url(business)
        if tenant:
            ac.query_config(business, {"name": tenant})
        else:
            ac.query_config(business)
    ac.exit_json()


if __name__ == '__main__':
    main()
