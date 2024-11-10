from __future__ import annotations
from typing import Any

import sqlalchemy as sa

from ckan import model
import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.collection import shared

from ckanext.check_link.model import Report


class Collection(p.SingletonPlugin):
    p.implements(shared.ICollection, inherit=True)

    def get_collection_factories(self) -> dict[str, shared.types.CollectionFactory]:
        return {
            "check-link-report": LinkCollection,
            "check-link-package-report": PackageLinkCollection,
            "check-link-organization-report": OrganizationLinkCollection,
        }


class LinkData(shared.data.ModelData[Report, "LinkCollection"]):
    model = Report
    is_scalar = True

    static_sources: dict[str, Any] = shared.configurable_attribute(
        default_factory=lambda self: {
            "resource": model.Resource,
            "package": model.Package,
        },
    )
    static_joins: list[tuple[str, Any, bool]] = shared.configurable_attribute(
        default_factory=lambda self: [
            ("resource", model.Resource.id == Report.resource_id, False),
            ("package", model.Resource.package_id == model.Package.id, False),
        ],
    )

    def alter_statement(self, stmt: sa.select):
        stmt = super().alter_statement(stmt)

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


class PackageLinkData(LinkData):
    package_id: str = shared.configurable_attribute()

    def alter_statement(self, stmt: sa.select):
        stmt = super().alter_statement(stmt)
        return stmt.where(self.static_sources["resource"].package_id == self.package_id)


class OrganizationLinkData(LinkData):
    organization_id: str = shared.configurable_attribute()

    def alter_statement(self, stmt: sa.select):
        stmt = super().alter_statement(stmt)
        return stmt.where(
            self.static_sources["package"].owner_org == self.organization_id
        )


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


class PackageLinkCollection(LinkCollection):
    DataFactory = PackageLinkData


class OrganizationLinkCollection(LinkCollection):
    DataFactory = OrganizationLinkData
