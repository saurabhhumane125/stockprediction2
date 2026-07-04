"""prediction_lifecycle

Revision ID: 941eaf239e7a
Revises: 323105764ab8
Create Date: 2026-07-04 23:21:27.717777
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "941eaf239e7a"
down_revision: Union[str, Sequence[str], None] = "323105764ab8"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ----------------------------
    # Step 1
    # ----------------------------

    op.add_column(
        "prediction_history",
        sa.Column(
            "prediction_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.add_column(
        "prediction_history",
        sa.Column(
            "evaluation_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.add_column(
        "prediction_history",
        sa.Column(
            "status",
            sa.String(20),
            nullable=True,
        ),
    )

    # ----------------------------
    # Step 2
    # Populate existing rows
    # ----------------------------

    op.execute(
        """
        UPDATE prediction_history
        SET
            prediction_date = DATE(created_at),
            status = 'COMPLETED'
        """
    )

    # ----------------------------
    # Step 3
    # Apply production constraints
    # ----------------------------

    op.alter_column(
        "prediction_history",
        "prediction_date",
        nullable=False,
    )

    op.alter_column(
        "prediction_history",
        "status",
        nullable=False,
    )

    op.create_index(
        "ix_prediction_history_prediction_date",
        "prediction_history",
        ["prediction_date"],
    )


def downgrade() -> None:

    op.drop_index(
        "ix_prediction_history_prediction_date",
        table_name="prediction_history",
    )

    op.drop_column(
        "prediction_history",
        "status",
    )

    op.drop_column(
        "prediction_history",
        "evaluation_date",
    )

    op.drop_column(
        "prediction_history",
        "prediction_date",
    )