"""Views module for the ckanext-check-link extension.

This module provides Flask blueprints and view functions for the administrative
UI components of the link checking extension, including the report page and CSV export.
These views enable administrators to monitor and manage link check reports through
a web interface.
"""

from __future__ import annotations

import csv
from typing import Any

from flask import Blueprint

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.logic import parse_params

from ckanext.collection import shared

# Define the columns for the CSV export of link check reports
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
    """Display link check reports for a specific organization.

    This view renders a page showing link check reports for all resources
    within a specific organization. It requires appropriate authorization
    and provides filtering options for the reports.

    Args:
        organization_id: The ID of the organization to show reports for

    Returns:
        Rendered HTML template with organization-specific link check reports
    """
    try:
        tk.check_access(
            "check_link_view_report_page",
            {"user": tk.g.user},
            {"organization_id": organization_id},
        )
    except tk.NotAuthorized:
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
    params[f"{col_name}:organization_id"] = org_dict["id"]

    collection = shared.get_collection(col_name, params)

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
    """Display link check reports for a specific package.

    This view renders a page showing link check reports for all resources
    within a specific package. It requires appropriate authorization
    and provides filtering options for the reports.

    Args:
        package_id: The ID of the package to show reports for

    Returns:
        Rendered HTML template with package-specific link check reports
    """
    try:
        tk.check_access(
            "check_link_view_report_page",
            {"user": tk.g.user},
            {"package_id": package_id},
        )
    except tk.NotAuthorized:
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
    params[f"{col_name}:package_id"] = pkg_dict["id"]
    collection = shared.get_collection(col_name, params)

    return tk.render(
        "check_link/package_report.html",
        {"collection": collection, "pkg_dict": pkg_dict},
    )


@bp.route("/check-link/report/global")
def report(
    organization_id: str | None = None,
    package_id: str | None = None,
):
    """Display global link check reports.

    This view renders the main page showing link check reports for the entire
    portal. It provides a comprehensive overview of broken links across all
    packages and resources. The view supports filtering and pagination.

    Args:
        organization_id: Optional organization ID to filter reports
        package_id: Optional package ID to filter reports

    Returns:
        Rendered HTML template with global link check reports
    """
    try:
        tk.check_access(
            "check_link_view_report_page",
            {"user": tk.g.user},
            {},
        )
    except tk.NotAuthorized:
        return tk.abort(403)

    col_name = "check-link-report"
    params: dict[str, Any] = {
        f"{col_name}:attached_only": True,
        f"{col_name}:exclude_state": ["available"],
    }
    params.update(parse_params(tk.request.args))

    collection = shared.get_collection(col_name, params)

    base_template = "check_link/base_admin.html"

    return tk.render(
        "check_link/global_report.html",
        {
            "collection": collection,
            "base_template": base_template,
        },
    )


class _FakeBuffer:
    """A fake buffer class for CSV writing that yields values instead of writing to a file.

    This internal class is used to generate CSV content without actually writing
    to a file, allowing the CSV content to be streamed as a response.
    """

    def write(self, value: Any):
        """Write method that returns the value instead of writing to a file.

        This method is designed to work with the csv.writer class to intercept
        the write operations and return the values instead of writing to a file.

        Args:
            value: The value to write

        Returns:
            The value that was "written"
        """
        return value


def _stream_csv(reports: Any):
    """Generate CSV rows for the provided reports.

    This internal function generates CSV content for link check reports,
    which can be used for exporting reports to CSV format. It includes
    caching for organization data to improve performance.

    Args:
        reports: Iterable of report dictionaries to convert to CSV

    Yields:
        CSV row strings formatted according to the defined column structure
    """
    writer = csv.writer(_FakeBuffer())

    # Write the header row
    yield writer.writerow(CSV_COLUMNS)
    # Cache organization data to avoid repeated database queries
    _org_cache = {}

    for report in reports:
        # Get the organization ID for this report
        owner_org = report["details"]["package"]["owner_org"]
        # Cache organization data to avoid repeated database queries
        if owner_org not in _org_cache:
            _org_cache[owner_org] = model.Group.get(owner_org)

        # Write the data row for this report
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
