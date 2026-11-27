import uuid
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.models.hotel import Hotel, Quarto
from app.models.interacao import Avaliacao, Favorito, Reserva
from app.models.usuario import Usuario

router = APIRouter(tags=["Reservas, avaliações e favoritos"])


class ReservaCreate(BaseModel):
    quarto_id: uuid.UUID
    data_checkin: date
    data_checkout: date
    adultos: int = Field(ge=1, le=20)
    criancas: int = Field(default=0, ge=0, le=20)


class ReservaPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    hotel_id: uuid.UUID
    quarto_id: uuid.UUID
    data_checkin: date
    data_checkout: date
    adultos: int
    criancas: int
    status: str
    valor_total: float


class AvaliacaoCreate(BaseModel):
    hotel_id: uuid.UUID
    nota: int = Field(ge=1, le=5)
    comentario: str = Field(min_length=3, max_length=2000)


class AvaliacaoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    usuario_id: uuid.UUID
    hotel_id: uuid.UUID
    nota: int
    comentario: str
    criada_em: datetime


class FavoritoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    hotel_id: uuid.UUID


@router.post("/reservas", response_model=ReservaPublic, status_code=status.HTTP_201_CREATED)
def criar_reserva(
    payload: ReservaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    hoje = date.today()
    if payload.data_checkin < hoje:
        raise HTTPException(status_code=422, detail="O check-in não pode estar no passado.")
    if payload.data_checkout <= payload.data_checkin:
        raise HTTPException(status_code=422, detail="O check-out deve ser posterior ao check-in.")

    quarto = db.query(Quarto).filter(Quarto.id == payload.quarto_id).with_for_update().first()
    if not quarto:
        raise HTTPException(status_code=404, detail="Quarto não encontrado.")
    if payload.adultos > quarto.max_adultos or payload.criancas > quarto.max_criancas:
        raise HTTPException(status_code=422, detail="A quantidade de hóspedes excede a capacidade do quarto.")

    conflito = db.query(Reserva).filter(
        Reserva.quarto_id == quarto.id,
        Reserva.status.in_(["pendente", "confirmada"]),
        Reserva.data_checkin < payload.data_checkout,
        Reserva.data_checkout > payload.data_checkin,
    ).first()
    if conflito:
        raise HTTPException(status_code=409, detail="Quarto indisponível para o período selecionado.")

    hotel = db.query(Hotel).filter(Hotel.id == quarto.hotel_id).first()
    noites = (payload.data_checkout - payload.data_checkin).days
    total = Decimal(str(quarto.preco_diaria)) * noites
    reserva = Reserva(
        usuario_id=usuario.id,
        hotel_id=hotel.id,
        quarto_id=quarto.id,
        data_checkin=payload.data_checkin,
        data_checkout=payload.data_checkout,
        adultos=payload.adultos,
        criancas=payload.criancas,
        status="pendente",
        valor_total=float(total),
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


@router.patch("/reservas/{reserva_id}/confirmar", response_model=ReservaPublic)
def confirmar_reserva(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_current_admin),
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).with_for_update().first()
    if not reserva:
        raise HTTPException(status_code=404, detail='Reserva não encontrada.')
    if reserva.status == 'cancelada':
        raise HTTPException(status_code=409, detail='Uma reserva cancelada não pode ser confirmada.')
    conflito = db.query(Reserva).filter(
        Reserva.quarto_id == reserva.quarto_id,
        Reserva.id != reserva.id,
        Reserva.status == 'confirmada',
        Reserva.data_checkin < reserva.data_checkout,
        Reserva.data_checkout > reserva.data_checkin,
    ).first()
    if conflito:
        raise HTTPException(status_code=409, detail='Já existe outra reserva confirmada neste período.')
    reserva.status = 'confirmada'
    db.commit()
    db.refresh(reserva)
    return reserva


@router.get("/reservas/minhas", response_model=list[ReservaPublic])
def listar_minhas_reservas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return db.query(Reserva).filter(Reserva.usuario_id == usuario.id).order_by(Reserva.criada_em.desc()).all()


@router.patch("/reservas/{reserva_id}/cancelar", response_model=ReservaPublic)
def cancelar_reserva(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    reserva = db.query(Reserva).filter(
        Reserva.id == reserva_id,
        Reserva.usuario_id == usuario.id,
    ).with_for_update().first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")
    if reserva.status == "cancelada":
        return reserva
    if reserva.data_checkin <= date.today():
        raise HTTPException(status_code=409, detail="Não é possível cancelar uma reserva que já começou.")
    reserva.status = "cancelada"
    db.commit()
    db.refresh(reserva)
    return reserva


@router.get("/hoteis/{hotel_id}/avaliacoes", response_model=list[AvaliacaoPublic])
def listar_avaliacoes(hotel_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Avaliacao).filter(Avaliacao.hotel_id == hotel_id).order_by(Avaliacao.criada_em.desc()).all()


@router.post("/avaliacoes", response_model=AvaliacaoPublic, status_code=status.HTTP_201_CREATED)
def criar_avaliacao(
    payload: AvaliacaoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    hotel = db.query(Hotel).filter(Hotel.id == payload.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel não encontrado.")
    estadia = db.query(Reserva).filter(
        Reserva.usuario_id == usuario.id,
        Reserva.hotel_id == payload.hotel_id,
        Reserva.status == "confirmada",
        Reserva.data_checkout <= date.today(),
    ).first()
    if not estadia:
        raise HTTPException(status_code=403, detail="Você precisa concluir uma hospedagem para avaliar este hotel.")
    avaliacao = db.query(Avaliacao).filter(
        Avaliacao.usuario_id == usuario.id,
        Avaliacao.hotel_id == payload.hotel_id,
    ).first()
    if avaliacao:
        raise HTTPException(status_code=409, detail="Você já avaliou este hotel.")
    avaliacao = Avaliacao(
        usuario_id=usuario.id,
        hotel_id=payload.hotel_id,
        nota=payload.nota,
        comentario=payload.comentario.strip(),
    )
    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)
    return avaliacao


@router.get("/favoritos", response_model=list[FavoritoPublic])
def listar_favoritos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return db.query(Favorito).filter(Favorito.usuario_id == usuario.id).all()


@router.put("/favoritos/{hotel_id}", response_model=FavoritoPublic)
def adicionar_favorito(
    hotel_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if not db.query(Hotel).filter(Hotel.id == hotel_id).first():
        raise HTTPException(status_code=404, detail="Hotel não encontrado.")
    favorito = db.query(Favorito).filter(
        Favorito.usuario_id == usuario.id,
        Favorito.hotel_id == hotel_id,
    ).first()
    if not favorito:
        favorito = Favorito(usuario_id=usuario.id, hotel_id=hotel_id)
        db.add(favorito)
        db.commit()
        db.refresh(favorito)
    return favorito


@router.delete("/favoritos/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_favorito(
    hotel_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    favorito = db.query(Favorito).filter(
        Favorito.usuario_id == usuario.id,
        Favorito.hotel_id == hotel_id,
    ).first()
    if favorito:
        db.delete(favorito)
        db.commit()
    return None
