from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base, hotel_comodidade

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class Comodidade(Base):
    __tablename__ = "comodidades"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    hoteis: Mapped[List["Hotel"]] = relationship(
        secondary=hotel_comodidade,
        back_populates="comodidades",
    )