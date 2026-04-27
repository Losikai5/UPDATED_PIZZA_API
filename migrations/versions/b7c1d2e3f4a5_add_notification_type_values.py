"""add notification type values

Revision ID: b7c1d2e3f4a5
Revises: 9b3d9ef9c0aa
Create Date: 2026-04-27
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "b7c1d2e3f4a5"
down_revision = "9b3d9ef9c0aa"
branch_labels = None
depends_on = None


NEW_VALUES = [
    "order_accepted",
    "order_in_transit",
    "order_completed",
    "order_cancelled",
]


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for value in NEW_VALUES:
            op.execute(
                f"ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # PostgreSQL does not support dropping enum values directly.
    pass