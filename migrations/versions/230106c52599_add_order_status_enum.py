"""add order status enum

Revision ID: 230106c52599
Revises: 1c0ef5f6f7a1
Create Date: 2026-04-23
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '230106c52599'
down_revision = '1c0ef5f6f7a1'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure any legacy orderstatus enum with incompatible labels is removed first.
    op.execute("""
        DO $$
        DECLARE
            labels text[];
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'orderstatus') THEN
                SELECT array_agg(e.enumlabel ORDER BY e.enumsortorder)
                INTO labels
                FROM pg_enum e
                JOIN pg_type t ON t.oid = e.enumtypid
                WHERE t.typname = 'orderstatus';

                IF labels IS DISTINCT FROM ARRAY['pending', 'order_accepted', 'in_transit', 'completed', 'cancelled'] THEN
                    DROP TYPE orderstatus;
                END IF;
            END IF;
        END
        $$;
    """)

    # 1. Define ENUM
    order_status_enum = sa.Enum(
        'pending',
        'order_accepted',
        'in_transit',
        'completed',
        'cancelled',
        name='orderstatus'
    )

    # 2. Create ENUM in PostgreSQL
    order_status_enum.create(op.get_bind(), checkfirst=True)

    # 3. Drop old VARCHAR default before type conversion
    op.execute("ALTER TABLE orders ALTER COLUMN order_status DROP DEFAULT")

    # 4. Convert column using explicit cast
    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN order_status
        TYPE orderstatus
        USING (
            CASE
                WHEN trim(BOTH '"' FROM lower(order_status)) = 'pending' THEN 'pending'
                WHEN trim(BOTH '"' FROM lower(order_status)) = 'order_accepted' THEN 'order_accepted'
                WHEN trim(BOTH '"' FROM lower(order_status)) = 'in_transit' THEN 'in_transit'
                WHEN trim(BOTH '"' FROM lower(order_status)) = 'completed' THEN 'completed'
                WHEN trim(BOTH '"' FROM lower(order_status)) = 'delivered' THEN 'completed'
                WHEN trim(BOTH '"' FROM lower(order_status)) = 'cancelled' THEN 'cancelled'
                WHEN trim(BOTH '"' FROM lower(order_status)) = 'canceled' THEN 'cancelled'
                ELSE 'pending'
            END
        )::orderstatus
    """)

    # 5. Re-apply default using enum type
    op.execute("ALTER TABLE orders ALTER COLUMN order_status SET DEFAULT 'pending'::orderstatus")


def downgrade():
    # 1. Drop enum default before converting back
    op.execute("ALTER TABLE orders ALTER COLUMN order_status DROP DEFAULT")

    # 2. Convert back to VARCHAR
    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN order_status
        TYPE VARCHAR
        USING order_status::text
    """)

    # 3. Re-apply VARCHAR default
    op.execute("ALTER TABLE orders ALTER COLUMN order_status SET DEFAULT 'pending'")

    # 4. Drop ENUM type
    order_status_enum = sa.Enum(name='orderstatus')
    order_status_enum.drop(op.get_bind(), checkfirst=True)