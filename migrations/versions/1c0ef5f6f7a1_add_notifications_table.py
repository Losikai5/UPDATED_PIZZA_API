"""add notifications table

Revision ID: 1c0ef5f6f7a1
Revises: 0d42d0315af7
Create Date: 2026-04-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "1c0ef5f6f7a1"
down_revision: Union[str, Sequence[str], None] = "0d42d0315af7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


notification_type_enum = sa.Enum(
    "verification",
    "maintenance",
    "order_placed",
    "order_delivered",
    "new_order",
    name="notificationtype",
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    # notification_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "notifications",
        sa.Column("uid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("notification_type", notification_type_enum, nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("user_uid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["user_uid"], ["users.uid"]),
        sa.PrimaryKeyConstraint("uid"),
    )
    op.create_index(op.f("ix_notifications_user_uid"), "notifications", ["user_uid"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_notifications_user_uid"), table_name="notifications")
    op.drop_table("notifications")

    bind = op.get_bind()
    notification_type_enum.drop(bind, checkfirst=True)
