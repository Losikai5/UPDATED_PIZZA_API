"""add total_price to orders

Revision ID: 9b3d9ef9c0aa
Revises: 230106c52599
Create Date: 2026-04-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b3d9ef9c0aa"
down_revision = "230106c52599"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "orders",
        sa.Column("total_price", sa.Float(), nullable=False, server_default="0"),
    )
    op.alter_column("orders", "total_price", server_default=None)


def downgrade():
    op.drop_column("orders", "total_price")
