"""adiciona campos de cidade e hotel

Revision ID: 270982051a5b
Revises: 002
Create Date: 2026-09-19 20:19:57.135994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '270982051a5b'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cidades",
        sa.Column("estado", sa.String(length=2), nullable=True),
    )

    op.add_column(
        "cidades",
        sa.Column("limite_territorial", sa.JSON(), nullable=True),
    )

    op.add_column(
        "hoteis",
        sa.Column("categoria_estrelas", sa.Integer(), nullable=True),
    )

    op.execute(
        "UPDATE cidades SET estado = 'CE' WHERE estado IS NULL"
    )

    op.execute(
        "UPDATE hoteis SET categoria_estrelas = 3 "
        "WHERE categoria_estrelas IS NULL"
    )

    op.alter_column(
        "cidades",
        "estado",
        existing_type=sa.String(length=2),
        nullable=False,
    )

    op.alter_column(
        "hoteis",
        "categoria_estrelas",
        existing_type=sa.Integer(),
        nullable=False,
    )
    
def downgrade() -> None:
    op.drop_column("hoteis", "categoria_estrelas")
    op.drop_column("cidades", "limite_territorial")
    op.drop_column("cidades", "estado")
