from __future__ import annotations

import csv
import datetime
from typing import TYPE_CHECKING, Any, Iterable

from flask import Blueprint

import ckan.authz as authz
import ckan.plugins.toolkit as tk
from ckan import model
from ckan.common import streaming_response
from ckan.lib.helpers import Page

if TYPE_CHECKING:
    from ckan.types import Context

CONFIG_BASE_TEMPLATE = "ckanext.check_link.report.base_template"
DEFAULT_BASE_TEMPLATE = "check_link/base_admin.html"

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


@bp.route("/check-link/report/global")
def report():
    if not authz.is_authorized_boolean(
        "check_link_view_report_page", {"user": tk.g.user}, {}
    ):
        return tk.abort(403)

    params: dict[str, Any] = {
        "attached_only": True,
        "exclude_state": ["available"],
    }

    fmt = tk.request.args.get("format")
    if fmt == "csv":
        resp = streaming_response(
            _stream_csv(
                _iterate_resuts("check_link_report_search", params, {"user": tk.g.user})
            ),
            mimetype="text/csv",
            with_context=True,
        )
        today = datetime.date.today()
        resp.headers[
            "content-disposition"
        ] = f'attachment; filename="VPSDDLinkReport-{today:%d%m%Y}.csv"'
        return resp

    try:
        page = max(1, tk.asint(tk.request.args.get("page", 1)))
    except ValueError:
        page = 1

    per_page = 10
    reports = tk.get_action("check_link_report_search")(
        {},
        dict(params, limit=per_page, offset=per_page * page - per_page),
    )

    def pager_url(*args: Any, **kwargs: Any):
        return tk.url_for("check_link.report", **kwargs)

    base_template = tk.config.get(CONFIG_BASE_TEMPLATE, DEFAULT_BASE_TEMPLATE)
    return tk.render(
        "check_link/report.html",
        {
            "base_template": base_template,
            "page": Page(
                reports["results"],
                url=pager_url,
                page=page,
                item_count=reports["count"],
                items_per_page=per_page,
                presliced_list=True,
            ),
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
