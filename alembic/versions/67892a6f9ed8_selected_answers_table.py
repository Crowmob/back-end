"""selected answers table

Revision ID: 67892a6f9ed8
Revises: 2d9be12f8b23
Create Date: 2025-08-27 12:12:51.731296

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "67892a6f9ed8"
down_revision: Union[str, Sequence[str], None] = "2d9be12f8b23"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "selected_answers",
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("answer_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["answer_id"], ["answers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["record_id"], ["records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_selected_answers_id"), "selected_answers", ["id"], unique=False
    )
    op.add_column("quizzes", sa.Column("frequency", sa.Integer(), nullable=False))


def downgrade() -> None:
    op.drop_column("quizzes", "frequency")
    op.drop_index(op.f("ix_selected_answers_id"), table_name="selected_answers")
    op.drop_table("selected_answers")
