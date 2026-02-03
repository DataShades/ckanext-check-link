"""Authentication functions for the ckanext-check-link extension.

This module contains authorization functions that determine whether a user
is allowed to perform specific actions related to link checking.
"""

from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import authz, types

CONFIG_ALLOW_USER = "ckanext.check_link.user_can_check_url"
DEFAULT_ALLOW_USER = False


def check_link_url_check(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to check URLs.

    Authorization depends on the 'ckanext.check_link.user_can_check_url' configuration.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    allow_user_checks = tk.asbool(
        tk.config.get(
            CONFIG_ALLOW_USER,
            DEFAULT_ALLOW_USER,
        )
    )
    return {"success": allow_user_checks and not authz.auth_is_anon_user(context)}


def check_link_resource_check(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to check a resource.

    Authorization is based on the user's permission to view the resource.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("resource_show", context, data_dict)


def check_link_package_check(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to check a package.

    Authorization is based on the user's permission to view the package.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("package_show", context, data_dict)


def check_link_organization_check(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to check an organization.

    Authorization is based on the user's permission to view the organization.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("organization_show", context, data_dict)


def check_link_group_check(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to check a group.

    Authorization is based on the user's permission to view the group.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("group_show", context, data_dict)


def check_link_user_check(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to check a user.

    Authorization is based on the user's permission to view the user profile.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("user_show", context, data_dict)


def check_link_search_check(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to perform search-based checks.

    Authorization is based on the user's permission to perform package search.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("package_search", context, data_dict)


def check_link_report_save(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to save reports.

    Only sysadmin users are authorized to save reports.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_report_show(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to view reports.

    Only sysadmin users are authorized to view reports.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_report_search(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to search reports.

    Only sysadmin users are authorized to search reports.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_report_delete(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to delete reports.

    Only sysadmin users are authorized to delete reports.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    return authz.is_authorized("sysadmin", context, data_dict)


def check_link_view_report_page(context: types.Context, data_dict: dict[str, Any]):
    """Check if the user is authorized to view the report page.

    Only sysadmin users are authorized to view the report page.

    Args:
        context: CKAN context dictionary
        data_dict: Action parameters dictionary

    Returns:
        Dictionary with 'success' key indicating authorization status
    """
    if pkg_id := data_dict.get("package_id"):
        return authz.is_authorized("package_update", context, {"id": pkg_id})

    if org_id := data_dict.get("organization_id"):
        return authz.is_authorized("organization_update", context, {"id": org_id})

    return authz.is_authorized("sysadmin", context, data_dict)
