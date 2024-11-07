"""add_ondelete_cascade_to_resource_id.

Revision ID: dad15b4f251a
Revises: 564f2016af51
Create Date: 2023-07-20 18:53:22.944540

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "dad15b4f251a"
down_revision = "564f2016af51"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("check_link_report_resource_id_fkey", "check_link_report")
    op.create_foreign_key(
        "check_link_report_resource_id_fkey",
        "check_link_report",
        "resource",
        ["resource_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("check_link_report_resource_id_fkey", "check_link_report")
    op.create_foreign_key(
        "check_link_report_resource_id_fkey",
        "check_link_report",
        "resource",
        ["resource_id"],
        ["id"],
    )
