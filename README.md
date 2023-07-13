# ansible-ac

The ansible-ac project provides an Ansible collection for managing and automating your HUAWEI iMaster NCE-Fabric Controller environment. It consists of a set of modules and roles for performing tasks related to AC.

This collection has been tested and supports iMaster NCE-Fabric Controller R22C10.
Modules supporting new features introduced in AC API in specific ACI versions might not be supported in earlier AC releases.

*Note: This collection is not compatible with versions of Ansible before v2.8.*

## Requirements
Ansible v2.9 or newer

## Install
Ansible must be installed
```
sudo pip install ansible
```

Install the collection
```
ansible-galaxy collection install huaweidatacom.nce_fabric
```
## Use
Once the collection is installed, you can use it in a playbook by specifying the full namespace path to the module, plugin and/or role.

```
- hosts: localhost
  gather_facts: no

  tasks:
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
```

### See Also:

* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

Ongoing development efforts and contributions to this collection are tracked as issues in this repository.
