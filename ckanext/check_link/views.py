from __future__ import annotations

import csv
from typing import TYPE_CHECKING, Any, Iterable

from flask import Blueprint

import ckan.plugins.toolkit as tk
from ckan import authz, model
from ckan.logic import parse_params

from ckanext.collection import shared

from ckanext.check_link.model import Report

if TYPE_CHECKING:
    from ckan.types import Context


CSV_COLUMNS = [
    "Data Record title",
    "Data Resource title",
    "Organisation",
    "State",
    "Error type",
    "Link to Data resource",
    "Date and time checked",
]

bp = Blueprint("check_link", __name__)

__all__ = ["bp"]


@bp.route("/organization/<organization_id>/check-link/report")
def organization_report(organization_id: str):
    if not authz.is_authorized_boolean(
        "check_link_view_report_page",
        {"user": tk.g.user},
        {"organization_id": organization_id},
    ):
        return tk.abort(403)

    try:
        org_dict = tk.get_action("organization_show")({}, {"id": organization_id})
    except tk.ObjectNotFound:
        return tk.abort(404)

    col_name = "check-link-organization-report"
    params: dict[str, Any] = {
        f"{col_name}:attached_only": True,
        f"{col_name}:exclude_state": ["available"],
    }
    params.update(parse_params(tk.request.args))

    data_settings: dict[str, Any] = {"organization_id": org_dict["id"]}
    collection = shared.get_collection(col_name, params, data_settings=data_settings)

    return tk.render(
        "check_link/organization_report.html",
        {
            "collection": collection,
            "group_dict": org_dict,
            "group_type": org_dict["type"],
        },
    )


@bp.route("/dataset/<package_id>/check-link/report")
def package_report(package_id: str):
    if not authz.is_authorized_boolean(
        "check_link_view_report_page", {"user": tk.g.user}, {"package_id": package_id}
    ):
        return tk.abort(403)

    try:
        pkg_dict = tk.get_action("package_show")({}, {"id": package_id})
    except tk.ObjectNotFound:
        return tk.abort(404)

    col_name = "check-link-package-report"
    params: dict[str, Any] = {
        f"{col_name}:attached_only": True,
        f"{col_name}:exclude_state": ["available"],
    }
    params.update(parse_params(tk.request.args))

    data_settings: dict[str, Any] = {"package_id": pkg_dict["id"]}
    collection = shared.get_collection(col_name, params, data_settings=data_settings)

    return tk.render(
        "check_link/package_report.html",
        {"collection": collection, "pkg_dict": pkg_dict},
    )


@bp.route("/check-link/report/global")
def report(
    organization_id: str | None = None,
    package_id: str | None = None,
):
    if not authz.is_authorized_boolean(
        "check_link_view_report_page", {"user": tk.g.user}, {}
    ):
        return tk.abort(403)

    col_name = "check-link-report"
    params: dict[str, Any] = {
        f"{col_name}:attached_only": True,
        f"{col_name}:exclude_state": ["available"],
    }
    params.update(parse_params(tk.request.args))

    data_settings = {}

    collection = shared.get_collection(col_name, params, data_settings=data_settings)

    base_template = "check_link/base_admin.html"

    return tk.render(
        "check_link/global_report.html",
        {
            "collection": collection,
            "base_template": base_template,
        },
    )


class _FakeBuffer:
    def write(self, value: Any):
        return value


def _stream_csv(reports: Iterable[dict[str, Any]]):
    writer = csv.writer(_FakeBuffer())

    yield writer.writerow(CSV_COLUMNS)
    _org_cache = {}

    for report in reports:
        owner_org = report["details"]["package"]["owner_org"]
        if owner_org not in _org_cache:
            _org_cache[owner_org] = model.Group.get(owner_org)

        yield writer.writerow(
            [
                report["details"]["package"]["title"],
                report["details"]["resource"]["name"] or "Unknown",
                _org_cache[owner_org] and _org_cache[owner_org].title,
                report["state"],
                report["details"]["explanation"],
                tk.url_for(
                    "resource.read",
                    id=report["package_id"],
                    resource_id=report["resource_id"],
                    _external=True,
                ),
                tk.h.render_datetime(report["created_at"], None, True),
            ]
        )


def _iterate_resuts(
    action: str,
    params: dict[str, Any],
    context: Context | None = None,
    offset: int = 0,
    chunk_size: int = 10,
) -> Iterable[dict[str, Any]]:
    while True:
        result = tk.get_action(action)(
            context or {},
            dict(params, limit=chunk_size, offset=offset),
        )
        yield from result["results"]
        offset += chunk_size
        if offset >= result["count"]:
            break
