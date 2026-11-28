
"""Concilia as duas implementacoes de reservas.

Revision ID: 5196cf4b4f93
Revises: 91af5a83eb21, 20261127_interacoes
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "5196cf4b4f93"
down_revision: Union[str, Sequence[str], None] = (
    "91af5a83eb21",
    "20261127_interacoes",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("reservas"):
        raise RuntimeError("A tabela reservas nao existe.")

    colunas = {
        coluna["name"]: coluna
        for coluna in inspector.get_columns("reservas")
    }

    # Padronizar os nomes usados pela API.
    renomeacoes = {
        "quantidade_adultos": "adultos",
        "quantidade_criancas": "criancas",
        "criado_em": "criada_em",
    }

    for antigo, novo in renomeacoes.items():
        if antigo in colunas:
            if novo in colunas:
                raise RuntimeError(
                    f"As colunas {antigo} e {novo} existem simultaneamente."
                )

            op.alter_column(
                "reservas",
                antigo,
                new_column_name=novo,
            )

    colunas = {
        coluna["name"]: coluna
        for coluna in sa.inspect(bind).get_columns("reservas")
    }

    obrigatorias = {
        "id",
        "usuario_id",
        "quarto_id",
        "data_checkin",
        "data_checkout",
        "adultos",
        "criancas",
        "status",
        "valor_total",
        "criada_em",
    }

    ausentes = obrigatorias - set(colunas)

    if ausentes:
        raise RuntimeError(
            f"Colunas obrigatorias ausentes: {sorted(ausentes)}"
        )

    # Recuperar o hotel a partir do quarto reservado.
    if "hotel_id" not in colunas:
        op.add_column(
            "reservas",
            sa.Column("hotel_id", sa.Uuid(), nullable=True),
        )

        op.execute(
            """
            UPDATE reservas AS r
            SET hotel_id = q.hotel_id
            FROM quartos AS q
            WHERE r.quarto_id = q.id
            """
        )

    pendentes = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM reservas WHERE hotel_id IS NULL"
        )
    ).scalar_one()

    if pendentes:
        raise RuntimeError(
            f"{pendentes} reservas ficaram sem hotel_id. "
            "A migracao foi interrompida para preservar os dados."
        )

    op.alter_column(
        "reservas",
        "hotel_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    # Preservar os campos adicionais da primeira implementacao.
    colunas = {
        coluna["name"]: coluna
        for coluna in sa.inspect(bind).get_columns("reservas")
    }

    if "idades_criancas" not in colunas:
        op.add_column(
            "reservas",
            sa.Column(
                "idades_criancas",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            ),
        )

    for campo in (
        "early_checkin",
        "late_checkout",
        "nao_reembolsavel",
    ):
        if campo not in colunas:
            op.add_column(
                "reservas",
                sa.Column(
                    campo,
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                ),
            )

    # Utilizar valor monetario com duas casas decimais.
    colunas = {
        coluna["name"]: coluna
        for coluna in sa.inspect(bind).get_columns("reservas")
    }

    tipo_valor = colunas["valor_total"]["type"]

    if not (
        isinstance(tipo_valor, sa.Numeric)
        and tipo_valor.precision == 10
        and tipo_valor.scale == 2
    ):
        op.alter_column(
            "reservas",
            "valor_total",
            existing_type=tipo_valor,
            type_=sa.Numeric(10, 2),
            postgresql_using="valor_total::numeric(10,2)",
        )

    # Padronizar as restricoes de verificacao.
    restricoes = {
        item["name"]
        for item in sa.inspect(bind).get_check_constraints("reservas")
    }

    renomear_restricoes = {
        "ck_reservas_status": "ck_reserva_status",
        "ck_reservas_periodo_valido": "ck_reserva_periodo",
    }

    for antigo, novo in renomear_restricoes.items():
        if antigo in restricoes:
            if novo in restricoes:
                raise RuntimeError(
                    f"Restricoes duplicadas: {antigo} e {novo}"
                )

            op.execute(
                f'ALTER TABLE reservas RENAME CONSTRAINT '
                f'"{antigo}" TO "{novo}"'
            )

    restricoes = {
        item["name"]
        for item in sa.inspect(bind).get_check_constraints("reservas")
    }

    for antigo in (
        "ck_reservas_minimo_adultos",
        "ck_reservas_minimo_criancas",
    ):
        if antigo in restricoes:
            op.drop_constraint(
                antigo,
                "reservas",
                type_="check",
            )

    if "ck_reserva_hospedes" not in restricoes:
        op.create_check_constraint(
            "ck_reserva_hospedes",
            "reservas",
            "adultos >= 1 AND criancas >= 0",
        )

    # Alinhar as chaves estrangeiras ao modelo atual.
    estrangeiras = sa.inspect(bind).get_foreign_keys("reservas")

    referencias = {
        "usuario_id": "usuarios",
        "hotel_id": "hoteis",
        "quarto_id": "quartos",
    }

    for coluna, tabela in referencias.items():
        encontradas = [
            chave
            for chave in estrangeiras
            if chave["constrained_columns"] == [coluna]
        ]

        if len(encontradas) > 1:
            raise RuntimeError(
                f"Multiplas chaves estrangeiras para {coluna}."
            )

        criar = not encontradas

        if encontradas:
            chave = encontradas[0]

            if chave["referred_table"] != tabela:
                raise RuntimeError(
                    f"Referencia inesperada em {coluna}."
                )

            comportamento = (
                (chave.get("options") or {}).get("ondelete") or ""
            ).upper()

            if comportamento != "CASCADE":
                if not chave["name"]:
                    raise RuntimeError(
                        f"Chave estrangeira sem nome em {coluna}."
                    )

                op.drop_constraint(
                    chave["name"],
                    "reservas",
                    type_="foreignkey",
                )
                criar = True

        if criar:
            op.create_foreign_key(
                f"fk_reservas_{coluna}",
                "reservas",
                tabela,
                [coluna],
                ["id"],
                ondelete="CASCADE",
            )

    # Garantir os indices esperados pela API.
    indices = {
        item["name"]
        for item in sa.inspect(bind).get_indexes("reservas")
    }

    for coluna in (
        "usuario_id",
        "hotel_id",
        "quarto_id",
    ):
        nome = f"ix_reservas_{coluna}"

        if nome not in indices:
            op.create_index(
                nome,
                "reservas",
                [coluna],
                unique=False,
            )

    # Garantir que o valor da reserva nao seja negativo.
    restricoes = {
        item["name"]
        for item in sa.inspect(bind).get_check_constraints("reservas")
    }

    if "ck_reservas_valor_nao_negativo" not in restricoes:
        op.create_check_constraint(
            "ck_reservas_valor_nao_negativo",
            "reservas",
            "valor_total >= 0",
        )

    # Manter o indice de consulta por quarto e periodo.
    indices = {
        item["name"]
        for item in sa.inspect(bind).get_indexes("reservas")
    }

    if "ix_reservas_quarto_datas" not in indices:
        op.create_index(
            "ix_reservas_quarto_datas",
            "reservas",
            ["quarto_id", "data_checkin", "data_checkout"],
        )

    # Remover o indice duplicado de usuario.
    if "ix_reservas_usuario" in indices:
        op.drop_index(
            "ix_reservas_usuario",
            table_name="reservas",
        )

    # Padronizar os nomes das chaves estrangeiras.
    for coluna in ("usuario_id", "hotel_id", "quarto_id"):
        antigo = f"reservas_{coluna}_fkey"
        novo = f"fk_reservas_{coluna}"

        estrangeiras = {
            item["name"]
            for item in sa.inspect(bind).get_foreign_keys("reservas")
        }

        if antigo in estrangeiras:
            if novo in estrangeiras:
                raise RuntimeError(
                    f"Chaves estrangeiras duplicadas: {antigo} e {novo}"
                )

            op.execute(
                f'ALTER TABLE reservas '
                f'RENAME CONSTRAINT "{antigo}" TO "{novo}"'
            )



def downgrade() -> None:
    raise RuntimeError(
        "A conciliacao nao pode ser revertida automaticamente "
        "sem risco de perda de dados. "
        "E necessario um procedimento de reversao especifico."
    )
