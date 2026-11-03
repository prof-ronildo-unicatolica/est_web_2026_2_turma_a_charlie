"""adiciona tabela de servicos adicionais

Revision ID: 7d95e210fde0
Revises: 8255266d83c3
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d95e210fde0"
down_revision: Union[str, Sequence[str], None] = "8255266d83c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "servicos_adicionais",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("preco", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("servicos_adicionais")