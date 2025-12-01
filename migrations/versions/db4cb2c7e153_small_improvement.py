"""small improvement

Revision ID: db4cb2c7e153
Revises: c50c470ed148
Create Date: 2025-11-21 02:07:46.513157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db4cb2c7e153'
down_revision: Union[str, None] = 'c50c470ed148'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert string values to integer with proper casting
    op.execute('ALTER TABLE orders ALTER COLUMN "Quantity" TYPE INTEGER USING "Quantity"::INTEGER')


def downgrade() -> None:
    # Convert back to string when downgrading
    op.execute('ALTER TABLE orders ALTER COLUMN "Quantity" TYPE VARCHAR USING "Quantity"::VARCHAR')