"""add menu items and menu item sizes

Revision ID: c81a50a3f86c
Revises: b7c1d2e3f4a5
Create Date: 2026-04-27

"""

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from alembic import op


revision = "c81a50a3f86c"
down_revision = "b7c1d2e3f4a5"
branch_labels = None
depends_on = None

pizzasize_enum = sa.Enum(
    "small", "medium", "large", "extra_large",
    name="pizzasize",
    create_type=False,
)

_CREATE_PIZZASIZE = sa.text("""
DO $$ BEGIN
    CREATE TYPE pizzasize AS ENUM ('small', 'medium', 'large', 'extra_large');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
""")

_DROP_PIZZASIZE = sa.text("DROP TYPE IF EXISTS pizzasize;")


def upgrade() -> None:
    op.execute(_CREATE_PIZZASIZE)

    op.create_table(
        "menu_items",
        sa.Column("uid", pg.UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.VARCHAR, nullable=False),
        sa.Column("flavour", sa.VARCHAR, nullable=False),
        sa.Column("description", sa.VARCHAR, nullable=False),
        sa.Column("is_available", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", pg.TIMESTAMP, server_default=sa.text("now()")),
        if_not_exists=True,
    )

    op.create_table(
        "menu_item_sizes",
        sa.Column("uid", pg.UUID, primary_key=True, nullable=False),
        sa.Column("pizza_size", pizzasize_enum, nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column(
            "menu_item_uid",
            pg.UUID,
            sa.ForeignKey("menu_items.uid"),
            nullable=False,
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("menu_item_sizes")
    op.drop_table("menu_items")
    op.execute(_DROP_PIZZASIZE)
