"""Main plugin module for the ckanext-check-link extension.

This module contains the CheckLinkPlugin class which implements various CKAN plugin
interfaces to provide link checking functionality for CKAN resources and arbitrary URLs.
"""

from __future__ import annotations

from typing import Any

from ckan import model
from ckan import plugins as p
from ckan.plugins import toolkit as tk

from . import implementations
from .logic import action
from .model import Report

CONFIG_CASCADE_DELETE = "ckanext.check_link.remove_reports_when_resource_deleted"


@tk.blanket.helpers
@tk.blanket.actions(action.get_actions)
@tk.blanket.cli
@tk.blanket.blueprints
@tk.blanket.auth_functions
class CheckLinkPlugin(
    implementations.Collection,
    p.SingletonPlugin,
):
    p.implements(p.IConfigurer)
    p.implements(p.IDomainObjectModification, inherit=True)

    def notify(self, entity: Any, operation: str) -> None:
        """Handle domain object modification notifications.

        When a resource is deleted, optionally remove its associated link check report
        based on the configuration setting.

        Args:
            entity: The domain object being modified
            operation: The type of operation being performed
        """
        if isinstance(entity, model.Resource) and entity.state == "deleted":
            if tk.asbool(tk.config.get(CONFIG_CASCADE_DELETE)):
                _remove_resource_report(entity.id)

    # IConfigurer
    def update_config(self, config_):
        """Add this extension's templates, public files and assets to CKAN's configuration."""
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "check_link")


def _remove_resource_report(resource_id: str):
    """Remove the link check report associated with a resource.

    Args:
        resource_id: The ID of the resource whose report should be removed
    """
    report = Report.by_resource_id(resource_id)
    if report:
        model.Session.delete(report)
