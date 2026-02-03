"""Command-line interface module for the ckanext-check-link extension.

This module provides Click commands for performing link checking operations
from the command line, including checking packages, resources, and managing reports.
The CLI interface is designed for bulk operations and automation tasks.
"""

from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Iterable
from itertools import islice
from typing import TypeVar

import click
import sqlalchemy as sa

import ckan.plugins.toolkit as tk
from ckan import model, types

from .model import Report

T = TypeVar("T")
log = logging.getLogger(__name__)

__all__ = ["check_link"]


@click.group(short_help="Check link availability")
def check_link():
    """Main command group for link checking operations.

    This command group provides access to all link checking CLI commands,
    including package checking, resource checking, and report management.
    """


@check_link.command()
@click.option("-d", "--include-draft", is_flag=True, help="Check draft packages as well")
@click.option("-p", "--include-private", is_flag=True, help="Check private packages as well")
@click.option(
    "-c",
    "--chunk",
    help="Number of packages that processed simultaneously",
    default=1,
    type=click.IntRange(
        1,
    ),
)
@click.option("-d", "--delay", default=0, help="Delay between requests", type=click.FloatRange(0))
@click.option("-t", "--timeout", default=10, help="Request timeout", type=click.FloatRange(0))
@click.option(
    "-o",
    "--organization",
    help="Check packages of specific organization",
)
@click.argument("ids", nargs=-1)
def check_packages(  # noqa: PLR0913
    include_draft: bool,
    include_private: bool,
    ids: tuple[str, ...],
    chunk: int,
    delay: float,
    timeout: float,
    organization: str | None,
):
    """Check every resource inside each package.

    This command performs comprehensive link checking for all resources within
    specified packages. It supports various filtering options and can process
    packages in configurable chunks for better performance with large datasets.
    The command provides real-time progress feedback with statistics on the
    distribution of link states (available, broken, etc.).

    Args:
        include_draft: Whether to include draft packages in the check
        include_private: Whether to include private packages in the check
        ids: Specific package IDs or names to check (checks all if empty)
        chunk: Number of packages to process simultaneously
        delay: Delay between requests in seconds
        timeout: Request timeout in seconds
        organization: Specific organization to check packages from
    """
    user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    context = types.Context(user=user["name"])

    check = tk.get_action("check_link_search_check")
    states = ["active"]

    if include_draft:
        states.append("draft")

    stmt = sa.select(model.Package.id).where(model.Package.state.in_(states))

    # Filter by organization if specified
    if organization:
        stmt = stmt.join(model.Group, model.Package.owner_org == model.Group.id).where(
            sa.or_(
                model.Group.id == organization,
                model.Group.name == organization,
            )
        )

    # Exclude private packages if not requested
    if not include_private:
        stmt = stmt.where(model.Package.private == False)

    # Filter by specific package IDs/names if provided
    if ids:
        stmt = stmt.where(model.Package.id.in_(ids) | model.Package.name.in_(ids))

    stats: Counter[str] = Counter()
    total = model.Session.scalar(sa.select(sa.func.count()).select_from(stmt))
    with click.progressbar(model.Session.scalars(stmt), length=total) as bar:
        while True:
            buff = _take(bar, chunk)
            if not buff:
                break

            result = check(
                tk.fresh_context(context),
                {
                    "fq": "id:({})".format(" OR ".join(buff)),
                    "save": True,
                    "clear_available": True,
                    "include_drafts": include_draft,
                    "include_private": include_private,
                    "skip_invalid": True,
                    "rows": chunk,
                    "link_patch": {"delay": delay, "timeout": timeout},
                },
            )
            stats.update(r["state"] for r in result)
            overview = (
                ", ".join(
                    f"{click.style(k, underline=True)}: {click.style(str(v), bold=True)}" for k, v in stats.items()
                )
                or "not available"
            )
            bar.label = f"Overview: {overview}"
            bar.update(chunk)

    click.secho("Done", fg="green")


def _take(seq: Iterable[T], size: int) -> list[T]:
    """Take a specified number of items from an iterable sequence.

    This internal utility function extracts a specified number of items
    from an iterable sequence, which is useful for processing data in chunks.

    Args:
        seq: The iterable sequence to take items from
        size: The number of items to take

    Returns:
        A list containing the taken items
    """
    return list(islice(seq, size))


@check_link.command()
@click.option("-d", "--delay", default=0, help="Delay between requests", type=click.FloatRange(0))
@click.option("-t", "--timeout", default=10, help="Request timeout", type=click.FloatRange(0))
@click.argument("ids", nargs=-1)
def check_resources(ids: tuple[str, ...], delay: float, timeout: float):
    """Check every resource on the portal.

    This command performs link checking for all active resources in the portal.
    It can be scoped to specific resources by providing their IDs as arguments.
    The command provides real-time progress feedback with statistics on the
    distribution of link states (available, broken, etc.).

    Args:
        ids: Specific resource IDs to check (checks all if empty)
        delay: Delay between requests in seconds
        timeout: Request timeout in seconds
    """
    user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    context: types.Context = {"user": user["name"]}

    check = tk.get_action("check_link_resource_check")
    # Query for active resources, optionally filtered by specific IDs
    q = model.Session.query(model.Resource.id).filter_by(state="active")
    if ids:
        q = q.filter(model.Resource.id.in_(ids))

    stats: Counter[str] = Counter()
    total = q.count()
    overview = "Not ready yet"
    with click.progressbar(q, length=total) as bar:
        for res in bar:
            bar.label = f"Current: {res.id}. Overview({total} total): {overview}"
            try:
                # Perform the link check for the current resource
                result = check(
                    tk.fresh_context(context),
                    {
                        "save": True,
                        "clear_available": True,
                        "id": res.id,
                        "link_patch": {"delay": delay, "timeout": timeout},
                    },
                )
            except tk.ValidationError:
                # Log validation errors and mark as exception state
                log.exception("Cannot check %s", res.id)
                result = {"state": "exception"}

            # Update statistics with the result
            stats[result["state"]] += 1
            overview = (
                ", ".join(
                    f"{click.style(k, underline=True)}: {click.style(str(v), bold=True)}" for k, v in stats.items()
                )
                or "not available"
            )
            bar.label = f"Current: {res.id}. Overview({total} total): {overview}"

    click.secho("Done", fg="green")


@check_link.command()
@click.option(
    "-o",
    "--orphans-only",
    is_flag=True,
    help="Only drop reports that point to an unexisting resource",
)
def delete_reports(orphans_only: bool):
    """Delete check-link reports.

    This command provides the ability to clean up link check reports from the database.
    It can delete all reports or only orphaned reports that point to resources that
    no longer exist or are not in an active state. This helps maintain a clean
    database by removing obsolete reports.

    Args:
        orphans_only: If True, only delete reports that point to non-existing resources
    """
    q = model.Session.query(Report)
    if orphans_only:
        # Find reports that are associated with a resource ID but where the resource
        # either doesn't exist anymore or is not in an active state
        q = q.outerjoin(model.Resource, Report.resource_id == model.Resource.id).filter(
            Report.resource_id.isnot(None),
            model.Resource.id.is_(None) | (model.Resource.state != "active"),
        )

    user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    context: types.Context = {"user": user["name"]}

    action = tk.get_action("check_link_report_delete")
    with click.progressbar(q, length=q.count()) as bar:
        for report in bar:
            # Delete each report individually
            action(tk.fresh_context(context), {"id": report.id})
