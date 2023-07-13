# -*- coding: utf-8 -*-

import uuid


def get_uuid():
    """
    Get uuid
    """
    return str(uuid.uuid4()).lower()


def is_success(info):
    """
    IS success
    """
    if info and info.get("status") in [200, 204]:
        return True
    else:
        return False


def filter_condition(datas, condition):
    """
    Filter condition
    """
    def conform_condition(data):
        for cond_name in condition:
            if data[cond_name] != condition[cond_name]:
                return False
        return True
    return list(filter(conform_condition, datas))
