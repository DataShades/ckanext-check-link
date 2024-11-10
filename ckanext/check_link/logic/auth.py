from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import authz, types

CONFIG_ALLOW_USER = "ckanext.check_link.user_can_check_url"
DEFAULT_ALLOW_USER = False


def check_link_url_check(context: types.Context, data_dict: dict[str, Any]):
    allow_user_checks = tk.asbool(
        tk.config.get(
            CONFIG_ALLOW_USER,
            DEFAULT_ALLOW_USER,
        )
    )
    return {"success": allow_user_checks and not authz.auth_is_anon_user(context)}


def check_link_resource_check(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("resource_show", context, data_dict)


def check_link_package_check(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("package_show", context, data_dict)


def check_link_organization_check(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("organization_show", context, data_dict)


def check_link_group_check(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("group_show", context, data_dict)


def check_link_user_check(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("user_show", context, data_dict)


def check_link_search_check(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("package_search", context, data_dict)


def check_link_report_save(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_report_show(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_report_search(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_report_delete(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_view_report_page(context: types.Context, data_dict: dict[str, Any]):
    if pkg_id := data_dict.get("package_id"):
        return authz.is_authorized("package_update", context, {"id": pkg_id})

    if org_id := data_dict.get("organization_id"):
        return authz.is_authorized("organization_update", context, {"id": org_id})

    return authz.is_authorized("sysadmin", context, data_dict)
