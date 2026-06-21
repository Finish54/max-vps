"""add_api_token_to_servers

Revision ID: c3f8a1d20e91
Revises: e7152afbe174
Create Date: 2026-05-29 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f8a1d20e91'
down_revision: Union[str, None] = 'fba5ae3d6764'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('servers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('api_token', sa.String(), nullable=True))
        # Сделать login и password nullable для обратной совместимости
        batch_op.alter_column('login', existing_type=sa.String(), nullable=True)
        batch_op.alter_column('password', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('servers', schema=None) as batch_op:
        batch_op.drop_column('api_token')
        batch_op.alter_column('login', existing_type=sa.String(), nullable=False)
        batch_op.alter_column('password', existing_type=sa.String(), nullable=False)
