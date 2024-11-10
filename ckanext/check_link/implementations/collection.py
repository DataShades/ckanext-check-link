from __future__ import annotations

import sqlalchemy as sa

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.collection import shared

from ckanext.check_link.model import Report


class Collection(p.SingletonPlugin):
    p.implements(shared.ICollection, inherit=True)

    def get_collection_factories(self) -> dict[str, shared.types.CollectionFactory]:
        return {
            "check-link-report": LinkCollection,
        }


class LinkData(shared.data.ModelData[Report, "LinkCollection"]):
    model = Report
    is_scalar = True

    def alter_statement(self, stmt: sa.select):
        params = self.attached.params
        if params.get("free_only"):
            stmt = stmt.where(self.model.resource_id.is_(None))

        if params.get("attached_only"):
            stmt = stmt.where(self.model.resource_id.isnot(None))

        if "exclude_state" in params:
            stmt = stmt.where(self.model.state.notin_(params["exclude_state"]))

        if "include_state" in params:
            stmt = stmt.where(self.model.state.in_(params["include_state"]))

        return stmt


class LinkHtmlSerializer(shared.serialize.HtmlSerializer["LinkCollection"]):
    main_template: str = shared.configurable_attribute(
        "check_link/snippets/collection_main.html"
    )
    record_template: str = shared.configurable_attribute(
        "check_link/snippets/collection_record.html"
    )
    pager_template: str = shared.configurable_attribute(
        "check_link/snippets/collection_pager.html"
    )


class LinkCollection(shared.collection.Collection):
    DataFactory = LinkData
    SerializerFactory = LinkHtmlSerializer
    ColumnsFactory = shared.columns.Columns.with_attributes(
        names=["resource_id", "state", "url", "code", "explanation"],
        labels={"resource_id": "Resource"},
        serializers={
            "resource_id": [
                (
                    lambda value, options, name, record, serializer: tk.url_for(
                        "resource.read",
                        id=record.package.name,
                        resource_id=record.resource.id,
                        _external=True,
                    ),
                    {},
                )
            ],
            "code": [
                (
                    lambda value, options, name, record, serializer: record.details.get(
                        "code"
                    ),
                    {},
                )
            ],
            "explanation": [
                (
                    lambda value, options, name, record, serializer: record.details.get(
                        "explanation"
                    ),
                    {},
                )
            ],
        },
    )
