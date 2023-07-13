# -*- coding: utf-8 -*-

import json

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.constants import BUSINESSES_URL_DIC, \
    BUSINESS_URL_DIC
from ansible_collections.huaweidatacom.nce_fabric.plugins.module_utils.utils import is_success, filter_condition


def ac_argument_spec():
    return dict(
        host=dict(
            type="str",
            required=True,
            aliases=["hostname"],
            fallback=(env_fallback, ["AC_HOST"]),
        ),
        port=dict(type="int", required=True, fallback=(env_fallback, ["AC_NORTH_PORT", "AC_PORT"])),
        username=dict(
            type="str",
            default="admin",
            aliases=["user"],
            fallback=(env_fallback, ["AC_USERNAME", "AC_USER"]),
        ),
        password=dict(
            type="str",
            no_log=True,
            fallback=(env_fallback, ["AC_PASSWORD", "AC_PASSWD"]),
        ),
        timeout=dict(type="int", default=30, fallback=(env_fallback, ["AC_TIMEOUT"])),
        output_path=dict(type="str", fallback=(env_fallback, ["AC_OUTPUT_PATH"])),
        validate_certs=dict(type="bool", default=False),
    )


def ac_annotation_spec():
    return dict(
        annotation=dict(
            type="str",
            default="orchestrator:ansible",
            fallback=(env_fallback, ["AC_ANNOTATION"]),
        ),
    )


class ACModule(object):
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.result = dict(changed=False, msg="")
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        self.config = dict()
        self.method = None
        self.response = None
        self.status = None
        self.url = None
        self.token = None
        # error output
        self.error = dict(code=None, text=None)

        if self.params.get("password"):
            # Perform password-based authentication, log on using password
            self.login()
        else:
            self.module.fail_json(msg="Parameter 'password' is required for authentication")

    def construct_url(self, business):
        """
        Construct url
        """
        self.url = "https://{host}:{port}{path}".format(path=BUSINESSES_URL_DIC[business], **self.module.params)

    def construct_object_url(self, business, object_id=None, object_name=None):
        """
        Construct url
        """
        if not object_id:
            self.module.fail_json(msg="Object %s doesn't exist" % object_name)
        self.url = "https://{host}:{port}{path}/{object_id}" \
            .format(path=BUSINESS_URL_DIC[business], object_id=object_id, **self.module.params)

    def set_config(self, config):
        """
        Set config
        """
        self.config = config

    def create_config(self):
        """
        Post config
        """
        resp, info = fetch_url(
            self.module,
            self.url,
            data=json.dumps(self.config),
            headers=self.headers,
            method="POST",
            timeout=self.params.get("timeout"),
        )

        self.response = info.get("msg")
        self.status = info.get("status")
        self.method = "POST"

        # Handle AC API response
        if is_success(info):
            self.result["changed"] = True
            self.result["msg"] = "Create success"
        else:
            # Connection error
            info["data"] = self.config
            self.module.fail_json(msg="Create failed for %(url)s. %(msg)s. %(data)s" % info)

    def update_config(self):
        """
        Update config
        """
        resp, info = fetch_url(
            self.module,
            self.url,
            data=json.dumps(self.config),
            headers=self.headers,
            method="PUT",
            timeout=self.params.get("timeout"),
        )

        self.response = info.get("msg")
        self.status = info.get("status")
        self.method = "PUT"

        # Handle AC API response
        if is_success(info):
            self.result["changed"] = True
            self.result["msg"] = "Update success"
        else:
            # Connection error
            info["data"] = self.config
            self.module.fail_json(msg="Update failed for %(url)s. %(msg)s. %(data)s" % info)

    def delete_config(self):
        """
        Delete config
        """
        resp, info = fetch_url(
            self.module,
            self.url,
            headers=self.headers,
            method="DELETE",
            timeout=self.params.get("timeout"),
        )

        self.response = info.get("msg")
        self.status = info.get("status")
        self.method = "DELETE"

        # Handle AC API response
        if is_success(info):
            self.result["changed"] = True
            self.result["msg"] = "Delete success"
        else:
            # Connection error
            self.module.fail_json(msg="Delete failed for %(url)s. %(msg)s" % info)

    def query_config(self, business, condition=None, uri=None):
        """
        Delete config
        """
        if not uri:
            uri = self.url
        resp, info = fetch_url(
            self.module,
            uri,
            headers=self.headers,
            method="GET",
            timeout=self.params.get("timeout"),
        )

        self.response = info.get("msg")
        self.status = info.get("status")
        self.method = "GET"
        # Handle AC API response
        if not is_success(info):
            # Connection error
            self.module.fail_json(msg="Query failed for %(url)s. %(msg)s" % info)
        datas = json.loads(resp.read()).get(business)
        if not condition or not datas:
            self.result["msg"] = datas
            return datas
        filter_data = filter_condition(datas, condition)
        self.result["msg"] = json.dumps(filter_data)
        return filter_data

    def operate_config(self, url, method, data):
        """
        Operate config
        """
        if not url.startswith("http"):
            url = "https://{host}:{port}{path}".format(path=url, **self.module.params)
        body = None
        if data:
            body = json.dumps(data) if isinstance(data, dict) else data

        resp, info = fetch_url(
            self.module,
            url,
            headers=self.headers,
            data=body,
            method=method,
            timeout=self.params.get("timeout"),
        )

        self.response = info.get("msg")
        self.status = info.get("status")
        self.method = method
        # Handle AC API response
        if is_success(info):
            self.result["changed"] = True
            self.result["msg"] = resp.read()
            self.result["body"] = body
        else:
            # Connection error
            info["data"] = data
            self.module.fail_json(msg="Operate failed for %(url)s. %(msg)s. %(data)s" % info)

    def login(self):
        """
        Log in to AC
        """
        # Perform login request
        url = "https://%(host)s:%(port)s/controller/v2/tokens" % self.params

        payload = {
            "userName": self.params.get("username"),
            "password": self.params.get("password")
        }
        resp, info = fetch_url(
            self.module,
            url,
            data=json.dumps(payload),
            headers=self.headers,
            method="POST",
            timeout=self.params.get("timeout"),
        )

        # Handle AC API response
        if is_success(info):
            # Retain cookie for later use
            self.token = json.loads(resp.read()).get("data").get("token_id")
            self.headers["X-ACCESS-TOKEN"] = self.token
        else:
            # Connection error
            self.module.fail_json(msg="Login in to AC failed. %(url)s. %(msg)s" % info)

    def query_id_by_name(self, business, name):
        """
        Query business id by business name
        """
        return self.query_id_by_condition(business, {"name": name})

    def query_id_by_condition(self, business, condition):
        """
        Query business id by condition
        """
        uri = "https://{host}:{port}{path}".format(path=BUSINESSES_URL_DIC[business], **self.module.params)
        datas = self.query_config(business, condition, uri)
        if not datas:
            self.module.fail_json(
                msg="Operate failed, %s(%s) doesn't exist." % (business, condition.get("name", condition)))
            return None
        if len(datas) > 1:
            self.module.fail_json(
                msg="Operate failed, %s(%s) isn't the only." % (business, condition.get("name", condition)))
        return datas[0].get("id", None)

    def exit_json(self):
        """
        exit json
        """
        self.result["method"] = self.method
        self.result["response"] = self.response
        self.result["status"] = self.status
        self.result["url"] = self.url
        self.module.exit_json(**self.result)

    def fail_json(self, msg):
        """
        fail json
        """
        self.module.fail_json(msg)

    def exit_token(self):
        """
        exit token
        """
        self.result["token"] = self.token
        self.module.exit_json(**self.result)
