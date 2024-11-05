from __future__ import annotations

from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model

from . import cli, views
from .logic import action, auth
from .model import Report

CONFIG_CASCADE_DELETE = "ckanext.check_link.remove_reports_when_resource_deleted"


@tk.blanket.helpers
class CheckLinkPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IBlueprint)
    p.implements(p.IClick)
    p.implements(p.IDomainObjectModification, inherit=True)

    def notify(self, entity: Any, operation: str) -> None:
        if (
            isinstance(entity, model.Resource)
            and entity.state == "deleted"
            and tk.asbool(tk.config.get(CONFIG_CASCADE_DELETE))
        ):
            _remove_resource_report(entity.id)

    # IConfigurer
    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "check_link")

    # IActions
    def get_actions(self):
        return action.get_actions()

    # IAuthFunctions
    def get_auth_functions(self):
        return auth.get_auth_functions()

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()

    # IClick
    def get_commands(self):
        return cli.get_commands()


def _remove_resource_report(resource_id: str):
    report = Report.by_resource_id(resource_id)
    if report:
        model.Session.delete(report)
