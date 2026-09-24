"""adiciona tabela de quartos

Revision ID: a633ea37cc50
Revises: 270982051a5b
Create Date: 2026-09-21 19:07:10.127190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a633ea37cc50'
down_revision: Union[str, None] = '270982051a5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quartos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("hotel_id", sa.UUID(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("preco_diaria", sa.Numeric(10, 2), nullable=False),
        sa.Column("max_adultos", sa.Integer(), nullable=False),
        sa.Column("max_criancas", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hotel_id"],
            ["hoteis.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("quartos")
