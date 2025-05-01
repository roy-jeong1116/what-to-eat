"""create notification field

Revision ID: f81a9fbb499e
Revises: 8df4b5c70601
Create Date: 2025-04-30 10:46:32.658427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f81a9fbb499e'
down_revision: Union[str, None] = '8df4b5c70601'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
