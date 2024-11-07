from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic import validate

from ckanext.toolbelt.decorators import Collector

from ckanext.check_link.logic import schema
from ckanext.check_link.model import Report

action: Any
action, get_actions = Collector("check_link").split()


@action
@validate(schema.report_save)
def report_save(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_report_save", context, data_dict)
    sess = context["session"]
    data_dict["details"].update(data_dict.pop("__extras", {}))

    try:
        existing = tk.get_action("check_link_report_show")(context, data_dict)
    except tk.ObjectNotFound:
        report = Report(**{**data_dict, "id": None})
        sess.add(report)
    else:
        report = sess.query(Report).filter(Report.id == existing["id"]).one()
        # this line update `created_at` value. Consider removing old report and
        # creating a brand new one instead, as it would be nice to have ID
        # regenerated as well
        report.touch()
        for k, v in data_dict.items():
            if k == "id":
                continue
            setattr(report, k, v)

    sess.commit()

    return report.dictize(context)


@action
@validate(schema.report_show)
def report_show(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_report_show", context, data_dict)

    if "id" in data_dict:
        report = (
            context["session"]
            .query(Report)
            .filter(Report.id == data_dict["id"])
            .one_or_none()
        )
    elif "resource_id" in data_dict:
        report = Report.by_resource_id(data_dict["resource_id"])
    elif "url" in data_dict:
        report = Report.by_url(data_dict["url"])
    else:
        raise tk.ValidationError(
            {"id": ["One of the following must be provided: id, resource_id, url"]}
        )

    if not report:
        raise tk.ObjectNotFound("report")

    return report.dictize(context)


@action
@validate(schema.report_search)
def report_search(context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    tk.check_access("check_link_report_search", context, data_dict)
    q = context["session"].query(Report)

    if data_dict["free_only"] and data_dict["attached_only"]:
        raise tk.ValidationError(
            {
                "free_only": [
                    "Filters `attached_only` and `free_only` cannot be applied"
                    " simultaneously"
                ]
            }
        )

    if data_dict["free_only"]:
        q = q.filter(Report.resource_id.is_(None))

    if data_dict["attached_only"]:
        q = q.filter(Report.resource_id.isnot(None))

    if "exclude_state" in data_dict:
        q = q.filter(Report.state.notin_(data_dict["exclude_state"]))

    if "include_state" in data_dict:
        q = q.filter(Report.state.in_(data_dict["include_state"]))

    count = q.count()
    q = q.order_by(Report.created_at.desc())
    q = q.limit(data_dict["limit"]).offset(data_dict["offset"])

    return {
        "count": count,
        "results": [
            r.dictize(dict(context, include_resource=True, include_package=True))
            for r in q
        ],
    }


@action
@validate(schema.report_delete)
def report_delete(context: types.Context, data_dict: dict[str, Any]):
    tk.check_access("check_link_report_delete", context, data_dict)
    sess = context["session"]

    report = tk.get_action("check_link_report_show")(context, data_dict)
    entity = sess.query(Report).filter(Report.id == report["id"]).one()

    sess.delete(entity)
    sess.commit()
    return entity.dictize(context)
