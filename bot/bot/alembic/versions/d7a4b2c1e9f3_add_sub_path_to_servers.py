"""add_sub_path_to_servers

Revision ID: d7a4b2c1e9f3
Revises: c3f8a1d20e91
Create Date: 2026-06-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7a4b2c1e9f3'
down_revision: Union[str, None] = 'c3f8a1d20e91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('servers', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('sub_path', sa.String(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table('servers', schema=None) as batch_op:
        batch_op.drop_column('sub_path')
