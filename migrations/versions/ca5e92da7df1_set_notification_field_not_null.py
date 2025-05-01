"""set notification field not null

Revision ID: ca5e92da7df1
Revises: 2ead9f3f6683
Create Date: 2025-04-30 10:59:33.852191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca5e92da7df1'
down_revision: Union[str, None] = '2ead9f3f6683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. 기존 NULL 값을 기본값으로 채우기
    op.execute("UPDATE users SET notification = TRUE WHERE notification IS NULL")

    # 2. nullable 제약 변경
    op.alter_column(
        'users',
        'notification',
        existing_type=sa.Boolean(),
        nullable=False
    )


def downgrade():
    # downgrade 시 nullable 다시 True로
    op.alter_column(
        'users',
        'notification',
        existing_type=sa.Boolean(),
        nullable=True
    )