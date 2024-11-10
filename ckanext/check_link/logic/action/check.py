from __future__ import annotations

import contextlib
import logging
from itertools import islice
from typing import Any, Iterable

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
def check_link_url_check(
    context: types.Context, data_dict: dict[str, Any]
) -> list[dict[str, Any]]:
    tk.check_access("check_link_url_check", context, data_dict)
    timeout: int = tk.asint(tk.config.get(CONFIG_TIMEOUT, DEFAULT_TIMEOUT))
    links: list[Link] = []

    kwargs: dict[str, Any] = data_dict["link_patch"]
    kwargs.setdefault("timeout", timeout)

    for url in data_dict["url"]:
        try:
            links.append(Link(url, **kwargs))
        except ValueError as e:
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
    tk.check_access("check_link_resource_check", context, data_dict)
    resource = tk.get_action("resource_show")(context, data_dict)

    result = tk.get_action("check_link_url_check")(
        context, {"url": [resource["url"]], "link_patch": data_dict["link_patch"]}
    )

    report = dict(
        result[0], resource_id=resource["id"], package_id=resource["package_id"]
    )

    if data_dict["save"]:
        _save_reports(context, [report], data_dict["clear_available"])

    return report


@action
@validate(schema.package_check)
def check_link_package_check(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_package_check", context, data_dict)
    return _search_check(
        context,
        "res_url:* (id:{0} OR name:{0})".format(solr_literal(data_dict["id"])),
        data_dict,
    )["reports"]


@action
@validate(schema.organization_check)
def check_link_organization_check(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_organization_check", context, data_dict)

    return _search_check(
        context,
        "res_url:* owner_org:{}".format(solr_literal(data_dict["id"])),
        data_dict,
    )["reports"]


@action
@validate(schema.group_check)
def check_link_group_check(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_group_check", context, data_dict)

    return _search_check(
        context, "res_url:* groups:{}".format(solr_literal(data_dict["id"])), data_dict
    )["reports"]


@action
@validate(schema.user_check)
def check_link_user_check(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_user_check", context, data_dict)

    return _search_check(
        context,
        "res_url:* creator_user_id:{}".format(solr_literal(data_dict["id"])),
        data_dict,
    )["reports"]


@action
@validate(schema.search_check)
def check_link_search_check(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_search_check", context, data_dict)

    return _search_check(context, data_dict["fq"], data_dict)["reports"]


def _search_check(
    context: types.Context, fq: str, data_dict: dict[str, Any]
) -> dict[str, Any]:
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

    patches, urls = zip(*pairs)

    result = tk.get_action("check_link_url_check")(
        context,
        {
            "url": urls,
            "skip_invalid": data_dict["skip_invalid"],
            "link_patch": data_dict["link_patch"],
        },
    )

    reports = [dict(report, **patch) for patch, report in zip(patches, result)]
    if data_dict["save"]:
        _save_reports(context, reports, data_dict["clear_available"])

    return {
        "reports": reports,
    }


def _iterate_search(
    context: types.Context, params: dict[str, Any]
) -> Iterable[dict[str, Any]]:
    params.setdefault("start", 0)

    while True:
        pack = tk.get_action("package_search")(context.copy(), params)
        if not pack["results"]:
            return

        yield from pack["results"]

        params["start"] += len(pack["results"])


def _save_reports(
    context: types.Context, reports: Iterable[dict[str, Any]], clear: bool
):
    save = tk.get_action("check_link_report_save")
    delete = tk.get_action("check_link_report_delete")

    for report in reports:
        if clear and report["state"] == "available":
            with contextlib.suppress(tk.ObjectNotFound):
                delete(context.copy(), report)
        else:
            save(context.copy(), report)
