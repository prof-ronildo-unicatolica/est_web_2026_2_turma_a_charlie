import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.tutorial import Base


class Reserva(Base):
    __tablename__ = "reservas"

    __table_args__ = (
        CheckConstraint(
            "data_checkout > data_checkin",
            name="ck_reservas_periodo_valido",
        ),
        CheckConstraint(
            "quantidade_adultos >= 1",
            name="ck_reservas_minimo_adultos",
        ),
        CheckConstraint(
            "quantidade_criancas >= 0",
            name="ck_reservas_minimo_criancas",
        ),
        CheckConstraint(
            "valor_total >= 0",
            name="ck_reservas_valor_nao_negativo",
        ),
        CheckConstraint(
            "status IN ('pendente', 'confirmada', 'cancelada')",
            name="ck_reservas_status",
        ),
        Index(
            "ix_reservas_quarto_datas",
            "quarto_id",
            "data_checkin",
            "data_checkout",
        ),
        Index("ix_reservas_usuario", "usuario_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )

    quarto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quartos.id", ondelete="RESTRICT"),
        nullable=False,
    )

    data_checkin: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    data_checkout: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    quantidade_adultos: Mapped[int] = mapped_column(
        nullable=False,
    )

    quantidade_criancas: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    idades_criancas: Mapped[list[int]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pendente",
    )

    early_checkin: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    late_checkout: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    nao_reembolsavel: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
