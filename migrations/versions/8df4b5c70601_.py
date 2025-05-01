"""empty message

Revision ID: 8df4b5c70601
Revises: f5726a841d5b
Create Date: 2025-04-29 14:34:18.144341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8df4b5c70601'
down_revision: Union[str, None] = 'f5726a841d5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
