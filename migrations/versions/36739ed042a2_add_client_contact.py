"""add client contact

Revision ID: 36739ed042a2
Revises: 51634ebc07a4
Create Date: 2026-06-17 15:14:44.899533

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "36739ed042a2"
down_revision: Union[str, Sequence[str], None] = "51634ebc07a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "shipment",
        sa.Column(
            "client_contact_email",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
    )
    op.add_column(
        "shipment",
        sa.Column("client_contact_phone", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("shipment", "client_contact_phone")
    op.drop_column("shipment", "client_contact_email")
