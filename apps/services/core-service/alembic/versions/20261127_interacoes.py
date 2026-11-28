"""adiciona reservas, avaliacoes e favoritos persistentes

Revision ID: 20261127_interacoes
Revises: cabf07da68d0
"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20261127_interacoes"
down_revision: Union[str, None] = "cabf07da68d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if not sa.inspect(op.get_bind()).has_table("reservas"):
        op.create_table(
        "reservas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("hotel_id", sa.Uuid(), nullable=False),
        sa.Column("quarto_id", sa.Uuid(), nullable=False),
        sa.Column("data_checkin", sa.Date(), nullable=False),
        sa.Column("data_checkout", sa.Date(), nullable=False),
        sa.Column("adultos", sa.Integer(), nullable=False),
        sa.Column("criancas", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("valor_total", sa.Float(), nullable=False),
        sa.Column("criada_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("data_checkout > data_checkin", name="ck_reserva_periodo"),
        sa.CheckConstraint("adultos >= 1 AND criancas >= 0", name="ck_reserva_hospedes"),
        sa.CheckConstraint("status IN ('pendente', 'confirmada', 'cancelada')", name="ck_reserva_status"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hotel_id"], ["hoteis.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quarto_id"], ["quartos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_reservas_usuario_id", "reservas", ["usuario_id"])
        op.create_index("ix_reservas_hotel_id", "reservas", ["hotel_id"])
        op.create_index("ix_reservas_quarto_id", "reservas", ["quarto_id"])

    op.create_table(
        "avaliacoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("hotel_id", sa.Uuid(), nullable=False),
        sa.Column("nota", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=False),
        sa.Column("criada_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("nota >= 1 AND nota <= 5", name="ck_avaliacao_nota"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hotel_id"], ["hoteis.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "hotel_id", name="uq_avaliacao_usuario_hotel"),
    )
    op.create_index("ix_avaliacoes_usuario_id", "avaliacoes", ["usuario_id"])
    op.create_index("ix_avaliacoes_hotel_id", "avaliacoes", ["hotel_id"])

    op.create_table(
        "favoritos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("hotel_id", sa.Uuid(), nullable=False),
        sa.Column("criada_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hotel_id"], ["hoteis.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "hotel_id", name="uq_favorito_usuario_hotel"),
    )
    op.create_index("ix_favoritos_usuario_id", "favoritos", ["usuario_id"])
    op.create_index("ix_favoritos_hotel_id", "favoritos", ["hotel_id"])




def downgrade() -> None:
    outra_aplicada = op.get_bind().execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM alembic_version
                WHERE version_num = '91af5a83eb21'
            )
            """
        )
    ).scalar_one()

    if outra_aplicada:
        raise RuntimeError(
            "Reversao bloqueada: a outra migracao "
            "de reservas tambem esta aplicada."
        )

    op.drop_table("favoritos")
    op.drop_table("avaliacoes")
    op.drop_table("reservas")