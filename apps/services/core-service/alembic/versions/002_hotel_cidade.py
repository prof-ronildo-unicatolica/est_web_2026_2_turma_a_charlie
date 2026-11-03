"""cria as tabelas cidades e hoteis (relacao 1:N)

Revision ID: 002
Revises: 001
Create Date: 2026-08-24 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# Identificadores de revisao, usados pelo Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ORDEM IMPORTA: 'cidades' primeiro. A FK de 'hoteis' aponta para ela,
    # e o PostgreSQL nao aceita referencia a uma tabela que ainda nao existe.
    op.create_table(
        "cidades",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )

    op.create_table(
        "hoteis",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("cidade_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["cidade_id"], ["cidades.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Indice na FK. O PostgreSQL indexa a PK automaticamente, mas NAO a chave
    # estrangeira -- e a consulta "hoteis desta cidade" filtra justamente por
    # ela. Sem indice, isso e varredura na tabela inteira.
    op.create_index("ix_hoteis_cidade_id", "hoteis", ["cidade_id"])


def downgrade() -> None:
    # ORDEM INVERSA do upgrade: derruba quem depende antes de quem e dependido.
    op.drop_index("ix_hoteis_cidade_id", table_name="hoteis")
    op.drop_table("hoteis")
    op.drop_table("cidades")