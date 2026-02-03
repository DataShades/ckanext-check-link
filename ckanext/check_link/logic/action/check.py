"""Action functions for link checking operations.

This module contains the core API action functions for checking the availability
of URLs, resources, packages, organizations, groups, and users.
"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Iterable
from itertools import islice
from typing import Any

from check_link import Link, check_all

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.lib.search.query import solr_literal
from ckan.logic import validate

from ckanext.toolbelt.decorators import Collector

from ckanext.check_link.logic import schema

CONFIG_TIMEOUT = "ckanext.check_link.check.timeout"
DEFAULT_TIMEOUT = 10

action: Any
log = logging.getLogger(__name__)
action, get_actions = Collector().split()


@action
@validate(schema.url_check)
def check_link_url_check(context: types.Context, data_dict: dict[str, Any]):
    """Check the availability of one or more URLs.

    Args:
        context: CKAN context dictionary
        data_dict: Dictionary containing:
            - url: List of URLs to check
            - save: Whether to save results to database (default: False)
            - clear_available: Whether to remove available reports when saving (default: False)
            - skip_invalid: Whether to skip invalid URLs instead of raising error (default: False)
            - link_patch: Additional parameters for link checking (default: {})

    Returns:
        List of dictionaries containing check results with keys: url, state, code, reason, explanation
    """
    tk.check_access("check_link_url_check", context, data_dict)
    timeout: int = tk.asint(tk.config.get(CONFIG_TIMEOUT, DEFAULT_TIMEOUT))
    links: list[Link] = []

    kwargs: dict[str, Any] = data_dict["link_patch"]
    kwargs.setdefault("timeout", timeout)

    for url in data_dict["url"]:
        try:
            links.append(Link(url, **kwargs))
        except ValueError as e:  # noqa: PERF203
            if data_dict["skip_invalid"]:
                log.debug("Skipping invalid url: %s", url)
            else:
                raise tk.ValidationError({"url": ["Must be a valid URL"]}) from e

    reports: list[dict[str, Any]] = [
        {
            "url": link.link,
            "state": link.state.name,
            "code": link.code,
            "reason": link.reason,
            "explanation": link.details,
        }
        for link in check_all(links)
    ]

    if data_dict["save"]:
        _save_reports(context, reports, data_dict["clear_available"])

    return reports


@action
@validate(schema.resource_check)
def check_link_resource_check(context: types.Context, data_dict: dict[str, Any]):
    """Check the availability of a specific resource.

    Args:
        context: CKAN context dictionary
        data_dict: Dictionary containing:
            - id: Resource ID to check
            - save: Whether to save results to database (default: False)
            - clear_available: Whether to remove available reports when saving (default: False)
            - link_patch: Additional parameters for link checking (default: {})

    Returns:
        Dictionary containing check result with resource metadata
    """
    tk.check_access("check_link_resource_check", context, data_dict)
    resource = tk.get_action("resource_show")(context, data_dict)

    result = tk.get_action("check_link_url_check")(
        context, {"url": [resource["url"]], "link_patch": data_dict["link_patch"]}
    )

    report = dict(result[0], resource_id=resource["id"], package_id=resource["package_id"])

    if data_dict["save"]:
        _save_reports(context, [report], data_dict["clear_available"])

    return report


@action
@validate(schema.package_check)
def check_link_package_check(context: types.Context, data_dict: dict[str, Any]):
    """Check all resources within a specific package.

    Args:
        context: CKAN context dictionary
        data_dict: Dictionary containing:
            - id: Package ID or name to check
            - save: Whether to save results to database (default: False)
            - clear_available: Whether to remove available reports when saving (default: False)
            - skip_invalid: Whether to skip invalid URLs (default: False)
            - include_drafts: Whether to include draft resources (default: False)
            - include_private: Whether to include private resources (default: False)
            - link_patch: Additional parameters for link checking (default: {})

    Returns:
        List of check results for all resources in the package
    """
    tk.check_access("check_link_package_check", context, data_dict)
    return _search_check(
        context,
        "res_url:* (id:{0} OR name:{0})".format(solr_literal(data_dict["id"])),
        data_dict,
    )["reports"]


@action
@validate(schema.organization_check)
def check_link_organization_check(context: types.Context, data_dict: dict[str, Any]):
    """Check all resources within a specific organization.

    Args:
        context: CKAN context dictionary
        data_dict: Dictionary containing:
            - id: Organization ID or name to check
            - save: Whether to save results to database (default: False)
            - clear_available: Whether to remove available reports when saving (default: False)
            - skip_invalid: Whether to skip invalid URLs (default: False)
            - include_drafts: Whether to include draft resources (default: False)
            - include_private: Whether to include private resources (default: False)
            - link_patch: Additional parameters for link checking (default: {})

    Returns:
        List of check results for all resources in the organization
    """
    tk.check_access("check_link_organization_check", context, data_dict)

    return _search_check(
        context,
        "res_url:* owner_org:{}".format(solr_literal(data_dict["id"])),
        data_dict,
    )["reports"]


@action
@validate(schema.group_check)
def check_link_group_check(context: types.Context, data_dict: dict[str, Any]):
    """Check all resources within a specific group.

    Args:
        context: CKAN context dictionary
        data_dict: Dictionary containing:
            - id: Group ID or name to check
            - save: Whether to save results to database (default: False)
            - clear_available: Whether to remove available reports when saving (default: False)
            - skip_invalid: Whether to skip invalid URLs (default: False)
            - include_drafts: Whether to include draft resources (default: False)
            - include_private: Whether to include private resources (default: False)
            - link_patch: Additional parameters for link checking (default: {})

    Returns:
        List of check results for all resources in the group
    """
    tk.check_access("check_link_group_check", context, data_dict)

    return _search_check(context, "res_url:* groups:{}".format(solr_literal(data_dict["id"])), data_dict)["reports"]


@action
@validate(schema.user_check)
def check_link_user_check(context: types.Context, data_dict: dict[str, Any]):
    """Check all resources created by a specific user.

    Args:
        context: CKAN context dictionary
        data_dict: Dictionary containing:
            - id: User ID or name to check
            - save: Whether to save results to database (default: False)
            - clear_available: Whether to remove available reports when saving (default: False)
            - skip_invalid: Whether to skip invalid URLs (default: False)
            - include_drafts: Whether to include draft resources (default: False)
            - include_private: Whether to include private resources (default: False)
            - link_patch: Additional parameters for link checking (default: {})

    Returns:
        List of check results for all resources created by the user
    """
    tk.check_access("check_link_user_check", context, data_dict)

    return _search_check(
        context,
        "res_url:* creator_user_id:{}".format(solr_literal(data_dict["id"])),
        data_dict,
    )["reports"]


@action
@validate(schema.search_check)
def check_link_search_check(context: types.Context, data_dict: dict[str, Any]):
    """Check resources based on a search query.

    Args:
        context: CKAN context dictionary
        data_dict: Dictionary containing:
            - fq: Search filter query (default: "*:*")
            - save: Whether to save results to database (default: False)
            - clear_available: Whether to remove available reports when saving (default: False)
            - skip_invalid: Whether to skip invalid URLs (default: False)
            - include_drafts: Whether to include draft resources (default: False)
            - include_private: Whether to include private resources (default: False)
            - start: Starting index for results (default: 0)
            - rows: Maximum number of packages to check (default: 10)
            - link_patch: Additional parameters for link checking (default: {})

    Returns:
        Dictionary with 'reports' key containing list of check results
    """
    tk.check_access("check_link_search_check", context, data_dict)

    return _search_check(context, data_dict["fq"], data_dict)["reports"]


def _search_check(context: types.Context, fq: str, data_dict: dict[str, Any]):
    """Perform a search-based link check operation.

    Args:
        context: CKAN context dictionary
        fq: Search filter query
        data_dict: Dictionary containing check parameters

    Returns:
        Dictionary with 'reports' key containing list of check results
    """
    params = {
        "fq": fq,
        "start": data_dict["start"],
        "include_drafts": data_dict["include_drafts"],
        # "include_deleted": data_dict["include_deleted"],
        "include_private": data_dict["include_private"],
    }

    pairs = [
        ({"resource_id": res["id"], "package_id": pkg["id"]}, res["url"])
        for pkg in islice(_iterate_search(context, params), data_dict["rows"])
        for res in pkg["resources"]
        if res["url"]
    ]

    if not pairs:
        return {"reports": []}

    patches, urls = zip(*pairs, strict=False)

    result = tk.get_action("check_link_url_check")(
        context,
        {
            "url": urls,
            "skip_invalid": data_dict["skip_invalid"],
            "link_patch": data_dict["link_patch"],
        },
    )

    reports = [dict(report, **patch) for patch, report in zip(patches, result, strict=False)]
    if data_dict["save"]:
        _save_reports(context, reports, data_dict["clear_available"])

    return {
        "reports": reports,
    }


def _iterate_search(context: types.Context, params: dict[str, Any]):
    """Iterate through search results for packages.

    Args:
        context: CKAN context dictionary
        params: Search parameters

    Yields:
        Package dictionaries from search results
    """
    params.setdefault("start", 0)

    while True:
        pack = tk.get_action("package_search")(context.copy(), params)
        if not pack["results"]:
            return

        yield from pack["results"]

        params["start"] += len(pack["results"])


def _save_reports(context: types.Context, reports: Iterable[dict[str, Any]], clear: bool):
    """Save link check reports to the database.

    Args:
        context: CKAN context dictionary
        reports: Iterable of report dictionaries to save
        clear: Whether to remove available reports when saving
    """
    save = tk.get_action("check_link_report_save")
    delete = tk.get_action("check_link_report_delete")

    for report in reports:
        if clear and report["state"] == "available":
            with contextlib.suppress(tk.ObjectNotFound):
                delete(context.copy(), report)
        else:
            save(context.copy(), report)
