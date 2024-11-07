from __future__ import annotations

from datetime import datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, backref, relationship
from typing_extensions import Self

from ckan import model, types
from ckan.lib.dictization import table_dictize
from ckan.lib.dictization.model_dictize import resource_dictize
from ckan.model.types import make_uuid

from .base import Base


class Report(Base):
    __table__ = sa.Table(
        "check_link_report",
        Base.metadata,
        sa.Column("id", sa.UnicodeText, primary_key=True, default=make_uuid),
        sa.Column("url", sa.UnicodeText, nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column(
            "resource_id",
            sa.UnicodeText,
            sa.ForeignKey(model.Resource.id),
            nullable=True,
            unique=True,
        ),
        sa.Column("details", JSONB, nullable=False, default=dict),
        sa.UniqueConstraint("url", "resource_id"),
    )

    id: Mapped[str]
    url: Mapped[str]
    state: Mapped[str]
    created_at: Mapped[datetime]
    resource_id: Mapped[str | None]
    details: Mapped[dict[str, Any]]

    package_id = association_proxy("resource", "package_id")
    package = association_proxy("resource", "package")

    resource = relationship(
        model.Resource,
        backref=backref(
            "check_link_report", cascade="all, delete-orphan", uselist=False
        ),
    )

    def touch(self):
        self.created_at = datetime.utcnow()

    def dictize(self, context: types.Context) -> dict[str, Any]:
        result = table_dictize(self, context, package_id=self.package_id)

        if context.get("include_resource") and self.resource_id:
            result["details"]["resource"] = resource_dictize(self.resource, context)

        if context.get("include_package") and self.package_id:
            result["details"]["package"] = resource_dictize(self.package, context)

        return result

    @classmethod
    def by_resource_id(cls, id_: str) -> Self | None:
        if not id_:
            return None

        return model.Session.query(cls).filter(cls.resource_id == id_).one_or_none()

    @classmethod
    def by_url(cls, url: str) -> Self | None:
        return (
            model.Session.query(cls)
            .filter(cls.resource_id.is_(None), cls.url == url)
            .one_or_none()
        )
