from __future__ import annotations

from flask import Blueprint
import ckan.plugins.toolkit as tk
from ckan.lib.helpers import Page

CONFIG_BASE_TEMPLATE = "ckanext.check_link.report.base_template"
CONFIG_REPORT_URL = "ckanext.check_link.report.url"


DEFAULT_BASE_TEMPLATE = "check_link/base_admin.html"
DEFAULT_REPORT_URL = "/check-link/report/global"


bp = Blueprint("check_link", __name__)

def get_blueprints():
    report_url = tk.config.get(CONFIG_REPORT_URL, DEFAULT_REPORT_URL)
    if report_url:
        bp.add_url_rule(report_url, view_func=report)

    return [bp]


def report():
    try:
        page = max(1, tk.asint(tk.request.args.get("page", 1)))
    except ValueError:
        page = 1

    per_page = 10
    reports = tk.get_action("check_link_report_search")({}, {
        "limit": per_page,
        "offset": per_page * page - per_page,
        "attached_only": True,
    })

    base_template = tk.config_get(
        CONFIG_BASE_TEMPLATE,
        DEFAULT_BASE_TEMPLATE
    )
    return tk.render("check_link/report.html", {
        "base_template": base_template,
        "page": Page(reports["results"], page=page, item_count=reports["count"], items_per_page=per_page, presliced_list=True)

    })
