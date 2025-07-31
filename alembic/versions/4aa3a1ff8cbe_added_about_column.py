"""added about column

Revision ID: 4aa3a1ff8cbe
Revises: b1e93f973592
Create Date: 2025-07-30 12:34:19.939516

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4aa3a1ff8cbe"
down_revision: Union[str, Sequence[str], None] = "b1e93f973592"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("about", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "about")
