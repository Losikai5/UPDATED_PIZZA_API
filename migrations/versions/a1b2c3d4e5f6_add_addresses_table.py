"""add_addresses_table

Revision ID: a1b2c3d4e5f6
Revises: 46c2ceb6b311
Create Date: 2026-05-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '46c2ceb6b311'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'addresses',
        sa.Column('uid', pg.UUID, primary_key=True, nullable=False),
        sa.Column('user_uid', pg.UUID, sa.ForeignKey('users.uid'), nullable=False),
        sa.Column('street_address', sa.VARCHAR, nullable=False),
        sa.Column('city', sa.VARCHAR, nullable=False),
        sa.Column('state', sa.VARCHAR, nullable=False),
        sa.Column('country', sa.VARCHAR, nullable=False),
        sa.Column('postal_code', sa.VARCHAR, nullable=False),
        sa.Column('is_default', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('now()')),
    )
    op.create_index('ix_addresses_user_uid', 'addresses', ['user_uid'])


def downgrade() -> None:
    op.drop_index('ix_addresses_user_uid', table_name='addresses')
    op.drop_table('addresses')
