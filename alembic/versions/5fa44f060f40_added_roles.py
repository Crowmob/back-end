"""added roles

Revision ID: 5fa44f060f40
Revises: f200bf145e3f
Create Date: 2025-08-11 10:57:42.561994

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "5fa44f060f40"
down_revision: Union[str, Sequence[str], None] = "f200bf145e3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "memberships", sa.Column("role", sa.String(length=50), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("memberships", "role")
