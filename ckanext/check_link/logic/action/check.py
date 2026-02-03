"""Action functions for link checking operations.

This module contains the core API action functions for checking the availability
of URLs, resources, packages, organizations, groups, and users. These actions
provide the foundation for all link checking functionality in the extension.
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

    This is the foundational action that checks the availability of URLs using
    the underlying check-link library. It can optionally save results to the
    database for historical tracking and analysis.

    Args:
        context: CKAN context dictionary containing user and session information
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

    # Execute the link checking for all collected links
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

    # Save reports to database if requested
    if data_dict["save"]:
        _save_reports(context, reports, data_dict["clear_available"])

    return reports


@action
@validate(schema.resource_check)
def check_link_resource_check(context: types.Context, data_dict: dict[str, Any]):
    """Check the availability of a specific resource.

    This action retrieves a resource by ID and checks the availability of its URL.
    It extends the basic URL checking functionality with resource-specific metadata
    and can optionally save the results to the database.

    Args:
        context: CKAN context dictionary containing user and session information
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

    This action performs comprehensive checking of all resources within a package.
    It uses search-based checking to efficiently process all resources and can
    include draft and private resources based on configuration.

    Args:
        context: CKAN context dictionary containing user and session information
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

    This action performs organization-wide link checking by finding all packages
    owned by the specified organization and checking all resources within them.
    It supports filtering for draft and private resources.

    Args:
        context: CKAN context dictionary containing user and session information
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

    This action performs group-based link checking by finding all packages
    associated with the specified group and checking all resources within them.
    It supports filtering for draft and private resources.

    Args:
        context: CKAN context dictionary containing user and session information
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

    This action performs user-based link checking by finding all packages
    created by the specified user and checking all resources within them.
    It supports filtering for draft and private resources.

    Args:
        context: CKAN context dictionary containing user and session information
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

    This action provides maximum flexibility by allowing link checking based
    on any CKAN search query. It finds packages matching the query and checks
    all resources within those packages. This is the most versatile checking
    method and serves as the foundation for other search-based checks.

    Args:
        context: CKAN context dictionary containing user and session information
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

    This internal function executes the core logic for search-based link checking.
    It searches for packages matching the specified query, extracts resource URLs,
    performs the link checks, and optionally saves the results to the database.

    Args:
        context: CKAN context dictionary containing user and session information
        fq: Search filter query to find packages
        data_dict: Dictionary containing check parameters including save options,
                  filtering options, and link checking parameters

    Returns:
        Dictionary with 'reports' key containing list of check results
    """
    # Prepare search parameters with filtering options
    params = {
        "fq": fq,
        "start": data_dict["start"],
        "include_drafts": data_dict["include_drafts"],
        # "include_deleted": data_dict["include_deleted"],
        "include_private": data_dict["include_private"],
    }

    # Extract resource URLs and their associated IDs from packages
    pairs = [
        ({"resource_id": res["id"], "package_id": pkg["id"]}, res["url"])
        for pkg in islice(_iterate_search(context, params), data_dict["rows"])
        for res in pkg["resources"]
        if res["url"]  # Only include resources with URLs
    ]

    if not pairs:
        return {"reports": []}

    # Separate patches and URLs for batch processing
    patches, urls = zip(*pairs, strict=False)

    # Perform URL checks for all extracted URLs
    result = tk.get_action("check_link_url_check")(
        context,
        {
            "url": urls,
            "skip_invalid": data_dict["skip_invalid"],
            "link_patch": data_dict["link_patch"],
        },
    )

    # Combine check results with resource/package IDs
    reports = [dict(report, **patch) for patch, report in zip(patches, result, strict=False)]

    # Save reports to database if requested
    if data_dict["save"]:
        _save_reports(context, reports, data_dict["clear_available"])

    return {
        "reports": reports,
    }


def _iterate_search(context: types.Context, params: dict[str, Any]):
    """Iterate through search results for packages.

    This internal generator function handles pagination of package search results,
    yielding packages one by one to avoid memory issues with large result sets.
    It automatically handles the pagination by incrementing the start parameter.

    Args:
        context: CKAN context dictionary containing user and session information
        params: Search parameters including query, start index, and filters

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

    This internal function handles the database operations for saving link check
    reports. It can optionally remove available reports when saving, which helps
    keep the database clean by removing successful checks while retaining failed ones.

    Args:
        context: CKAN context dictionary containing user and session information
        reports: Iterable of report dictionaries to save to the database
        clear: Whether to remove available reports when saving (keeps only failed checks)
    """
    save = tk.get_action("check_link_report_save")
    delete = tk.get_action("check_link_report_delete")

    for report in reports:
        if clear and report["state"] == "available":
            with contextlib.suppress(tk.ObjectNotFound):
                delete(context.copy(), report)
        else:
            save(context.copy(), report)
