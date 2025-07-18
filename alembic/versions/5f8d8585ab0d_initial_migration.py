"""Initial migration

Revision ID: 5f8d8585ab0d
Revises:
Create Date: 2025-07-17 14:41:15.485376

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "5f8d8585ab0d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column(
        "users",
        "created_at",
        server_default=sa.text("now()"),
        existing_type=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.drop_constraint(op.f("users_email_key"), "users", type_="unique")
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    op.drop_column("users", "date_of_birth")
    op.drop_column("users", "gender")


def downgrade() -> None:
    op.add_column(
        "users", sa.Column("gender", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "users",
        sa.Column(
            "date_of_birth", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
    )
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.create_unique_constraint(
        op.f("users_email_key"), "users", ["email"], postgresql_nulls_not_distinct=False
    )
    op.alter_column(
        "users",
        "created_at",
        server_default=None,
        existing_type=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.drop_column("users", "updated_at")
