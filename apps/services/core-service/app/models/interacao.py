import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.tutorial import Base


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("data_checkout > data_checkin", name="ck_reserva_periodo"),
        CheckConstraint("adultos >= 1 AND criancas >= 0", name="ck_reserva_hospedes"),
        CheckConstraint("status IN ('pendente', 'confirmada', 'cancelada')", name="ck_reserva_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    hotel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hoteis.id", ondelete="CASCADE"), nullable=False, index=True)
    quarto_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quartos.id", ondelete="CASCADE"), nullable=False, index=True)
    data_checkin: Mapped[date] = mapped_column(Date, nullable=False)
    data_checkout: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    adultos: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    criancas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmada")
    valor_total: Mapped[float] = mapped_column(nullable=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Avaliacao(Base):
    __tablename__ = "avaliacoes"
    __table_args__ = (
        CheckConstraint("nota >= 1 AND nota <= 5", name="ck_avaliacao_nota"),
        UniqueConstraint("usuario_id", "hotel_id", name="uq_avaliacao_usuario_hotel"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    hotel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hoteis.id", ondelete="CASCADE"), nullable=False, index=True)
    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str] = mapped_column(Text, nullable=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Favorito(Base):
    __tablename__ = "favoritos"
    __table_args__ = (UniqueConstraint("usuario_id", "hotel_id", name="uq_favorito_usuario_hotel"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    hotel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hoteis.id", ondelete="CASCADE"), nullable=False, index=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
