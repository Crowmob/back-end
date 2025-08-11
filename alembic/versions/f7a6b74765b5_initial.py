"""initial

Revision ID: f7a6b74765b5
Revises:
Create Date: 2025-08-01 10:53:25.545766

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7a6b74765b5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.Column("owner", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_companies_id"), table_name="companies")
    op.drop_table("companies")
