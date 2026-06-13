"""add destination column

Revision ID: 6332e9521b6b
Revises: a45b6fcda89f
Create Date: 2026-06-13 15:21:31.155410

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6332e9521b6b"
down_revision: Union[str, Sequence[str], None] = "a45b6fcda89f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "shipment",
        sa.Column("destination", sa.INTEGER, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "shipment",
        "destination",
    )
