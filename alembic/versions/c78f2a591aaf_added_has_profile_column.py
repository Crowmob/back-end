"""added has_profile column

Revision ID: c78f2a591aaf
Revises: 4aa3a1ff8cbe
Create Date: 2025-07-30 16:01:19.820494

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c78f2a591aaf"
down_revision: Union[str, Sequence[str], None] = "4aa3a1ff8cbe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("has_profile", sa.Boolean(), nullable=False))


def downgrade() -> None:
    op.drop_column("users", "has_profile")
