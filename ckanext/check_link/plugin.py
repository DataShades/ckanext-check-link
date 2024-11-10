from __future__ import annotations

from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model

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
        if (
            isinstance(entity, model.Resource)
            and entity.state == "deleted"
            and tk.asbool(tk.config.get(CONFIG_CASCADE_DELETE))
        ):
            _remove_resource_report(entity.id)

    # IConfigurer
    def update_config(self, config_: Any):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "check_link")


def _remove_resource_report(resource_id: str):
    report = Report.by_resource_id(resource_id)
    if report:
        model.Session.delete(report)
