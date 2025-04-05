"""Model Post Location Added SECOND TIME

Revision ID: ef4fb5a7888b
Revises: 00469211bf87
Create Date: 2025-04-05 20:45:55.850644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef4fb5a7888b'
down_revision: Union[str, None] = '00469211bf87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('location', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'location')
    # ### end Alembic commands ###
