"""added records

Revision ID: c2894dab5c67
Revises: 591c648ab3c1
Create Date: 2025-08-20 16:17:54.387938

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2894dab5c67"
down_revision: Union[str, Sequence[str], None] = "591c648ab3c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "records",
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["participant_id"], ["quiz_participants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_records_id"), "records", ["id"], unique=False)
    op.add_column(
        "questions", sa.Column("correct_answers", sa.Integer(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("questions", "correct_answers")
    op.drop_index(op.f("ix_records_id"), table_name="records")
    op.drop_table("records")
