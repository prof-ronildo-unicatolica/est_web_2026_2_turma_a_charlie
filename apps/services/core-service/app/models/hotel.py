from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import JSON, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base, hotel_comodidade

if TYPE_CHECKING:
    from app.models.comodidade import Comodidade

class Cidade(Base):
    __tablename__ = "cidades"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    limite_territorial: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    hoteis: Mapped[List["Hotel"]] = relationship(
        back_populates="cidade",
        cascade="all, delete-orphan",
    )


class Hotel(Base):
    __tablename__ = "hoteis"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    cidade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cidades.id", ondelete="CASCADE"),
        nullable=False,
    )

    categoria_estrelas: Mapped[int] = mapped_column(
        nullable=False,
    )

    cidade: Mapped["Cidade"] = relationship(
        back_populates="hoteis",
    )

    quartos: Mapped[List["Quarto"]] = relationship(
        back_populates="hotel",
        cascade="all, delete-orphan",
    )

    comodidades: Mapped[List["Comodidade"]] = relationship(
        secondary=hotel_comodidade,
        back_populates="hoteis",
    )


class Quarto(Base):
    __tablename__ = "quartos"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    hotel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hoteis.id", ondelete="CASCADE"),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    preco_diaria: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    max_adultos: Mapped[int] = mapped_column(
        nullable=False,
    )

    max_criancas: Mapped[int] = mapped_column(
        nullable=False,
    )

    hotel: Mapped["Hotel"] = relationship(
        back_populates="quartos",
    )