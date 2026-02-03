"""Main plugin module for the ckanext-check-link extension.

This module contains the CheckLinkPlugin class which implements various CKAN plugin
interfaces to provide link checking functionality for CKAN resources and arbitrary URLs.
The plugin handles configuration, domain object modifications, and registers all
extension components including helpers, actions, CLI commands, blueprints, and auth functions.
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
    """Main plugin class for the link checking extension.

    This class implements CKAN's plugin interfaces to provide comprehensive
    link checking functionality. It handles configuration setup, domain object
    modifications for resource deletion events, and registers all extension
    components through blanket decorators.
    """
    p.implements(p.IConfigurer)
    p.implements(p.IDomainObjectModification, inherit=True)

    def notify(self, entity: Any, operation: str) -> None:
        """Handle domain object modification notifications.

        When a resource is deleted, optionally remove its associated link check report
        based on the configuration setting. This prevents orphaned reports from
        accumulating in the database.

        Args:
            entity: The domain object being modified (expected to be a Resource)
            operation: The type of operation being performed (create, update, delete)
        """
        # Only process resource deletion events
        if isinstance(entity, model.Resource) and entity.state == "deleted":
            # Check if cascade deletion is enabled in configuration
            if tk.asbool(tk.config.get(CONFIG_CASCADE_DELETE)):
                _remove_resource_report(entity.id)

    # IConfigurer
    def update_config(self, config_):
        """Add this extension's templates, public files and assets to CKAN's configuration.

        This method registers the extension's templates, static files, and assets
        with CKAN's configuration system, making them available to the application.

        Args:
            config_: The CKAN configuration dictionary to update
        """
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "check_link")


def _remove_resource_report(resource_id: str):
    """Remove the link check report associated with a resource.

    This internal function handles the removal of link check reports when
    a resource is deleted, based on the cascade deletion configuration setting.

    Args:
        resource_id: The ID of the resource whose report should be removed
    """
    report = Report.by_resource_id(resource_id)
    if report:
        model.Session.delete(report)
