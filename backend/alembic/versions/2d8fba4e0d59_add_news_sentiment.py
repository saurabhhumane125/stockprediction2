"""add_news_sentiment"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision = "2d8fba4e0d59"
down_revision = "7bef20771dac"
branch_labels = None
depends_on = None


sentiment_enum = sa.Enum(
    "POSITIVE",
    "NEGATIVE",
    "NEUTRAL",
    name="sentimenttype",
)


def upgrade():

    sentiment_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "news",
        sa.Column(
            "sentiment",
            sentiment_enum,
            nullable=True,
        ),
    )

    op.add_column(
        "news",
        sa.Column(
            "sentiment_score",
            sa.Float(),
            nullable=True,
        ),
    )


def downgrade():

    op.drop_column(
        "news",
        "sentiment_score",
    )

    op.drop_column(
        "news",
        "sentiment",
    )

    sentiment_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )