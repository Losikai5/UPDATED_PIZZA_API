"""add menu tables

Revision ID: ea01ecd3d23c
Revises: c81a50a3f86c
Create Date: 2026-05-06 20:51:48.005509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ea01ecd3d23c'
down_revision: Union[str, Sequence[str], None] = 'c81a50a3f86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# postgresql.ENUM with create_type=False reuses an existing DB type without
# trying to CREATE or DROP it automatically — safe when the type already exists.
pizzasize_enum = postgresql.ENUM(
    "small", "medium", "large", "extra_large",
    name="pizzasize",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    # Idempotent enum creation — no-op if type already exists
    op.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE pizzasize AS ENUM ('small', 'medium', 'large', 'extra_large');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """))

    op.create_table(
        "menu_items",
        sa.Column("uid", sa.UUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("flavour", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("uid"),
    )
    op.create_table(
        "menu_item_sizes",
        sa.Column("uid", sa.UUID(), nullable=False),
        sa.Column("pizza_size", pizzasize_enum, nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("menu_item_uid", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["menu_item_uid"], ["menu_items.uid"]),
        sa.PrimaryKeyConstraint("uid"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("menu_item_sizes")
    op.drop_table("menu_items")
    op.execute(sa.text("DROP TYPE IF EXISTS pizzasize;"))
