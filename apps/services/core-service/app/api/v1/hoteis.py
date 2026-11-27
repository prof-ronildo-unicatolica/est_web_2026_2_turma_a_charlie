import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin

from app.core.database import get_db, get_mongo_db
from app.mensagens import HOTEL_NAO_ENCONTRADO
from app.models.comodidade import Comodidade
from app.models.hotel import Cidade, Hotel
from app.models.interacao import Reserva
from app.repositories.catalogo_repository import CatalogoRepository
from app.schemas.hotel import HotelCreateSchema, HotelResponseSchema, HotelUpdateSchema
from app.services.catalogo_sync_service import CatalogoSyncService
from app.services.hotel_service import HotelService

router = APIRouter(
    prefix="/hoteis",
    tags=["Hoteis"],
)


@router.post(
    "",
    response_model=HotelResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def criar_hotel(
    payload: HotelCreateSchema,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _admin=Depends(get_current_admin),
):
    service = HotelService(db, mongo_db)

    cidade = db.query(Cidade).filter(
        Cidade.id == payload.cidade_id
    ).first()

    if not cidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidade não encontrada.",
        )

    return await service.create(payload)


@router.get(
    "",
    response_model=list[HotelResponseSchema],
)
def listar_hoteis(
    cidade_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    service = HotelService(db, mongo_db)

    if cidade_id:
        cidade = db.query(Cidade).filter(
            Cidade.id == cidade_id
        ).first()

        if not cidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cidade não encontrada.",
            )

        return service.list_by_cidade(cidade_id)

    return service.list()


@router.get(
    "/{hotel_id}",
    response_model=HotelResponseSchema,
)
def obter_hotel(
    hotel_id: uuid.UUID,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    service = HotelService(db, mongo_db)

    hotel = service.get_by_id(hotel_id)

    if not hotel:
        raise HTTPException(
            status_code=404,
            detail=HOTEL_NAO_ENCONTRADO,
        )

    return hotel


@router.get(
    "/cidades/{cidade_id}/hoteis",
    response_model=list[HotelResponseSchema],
)
def listar_hoteis_por_cidade(
    cidade_id: uuid.UUID,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    cidade = db.query(Cidade).filter(
        Cidade.id == cidade_id
    ).first()

    if not cidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidade não encontrada.",
        )

    service = HotelService(db, mongo_db)

    return service.list_by_cidade(cidade_id)


@router.patch("/{hotel_id}", response_model=HotelResponseSchema)
async def atualizar_hotel(
    hotel_id: uuid.UUID,
    payload: HotelUpdateSchema,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _admin=Depends(get_current_admin),
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail=HOTEL_NAO_ENCONTRADO)

    dados = payload.model_dump(exclude_unset=True)
    if not dados or any(valor is None for campo, valor in dados.items() if campo != "comodidade_ids"):
        raise HTTPException(status_code=422, detail="Informe campos válidos para atualização.")

    if "cidade_id" in dados:
        cidade = db.query(Cidade).filter(Cidade.id == dados["cidade_id"]).first()
        if not cidade:
            raise HTTPException(status_code=404, detail="Cidade não encontrada.")

    if "comodidade_ids" in dados:
        ids = dados.pop("comodidade_ids") or []
        comodidades = db.query(Comodidade).filter(Comodidade.id.in_(ids)).all() if ids else []
        if {item.id for item in comodidades} != set(ids):
            raise HTTPException(status_code=422, detail="Uma ou mais comodidades não foram encontradas.")
        hotel.comodidades = comodidades

    for campo, valor in dados.items():
        setattr(hotel, campo, valor)

    db.commit()
    db.refresh(hotel)
    await CatalogoSyncService(db, mongo_db).sincronizar_hotel(hotel.id)
    return hotel


@router.delete("/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_hotel(
    hotel_id: uuid.UUID,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _admin=Depends(get_current_admin),
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail=HOTEL_NAO_ENCONTRADO)
    possui_reservas = db.query(Reserva).filter(Reserva.hotel_id == hotel_id).first()
    if possui_reservas:
        raise HTTPException(status_code=409, detail="Não é possível excluir um hotel que possui histórico de reservas.")
    db.delete(hotel)
    db.commit()
    await CatalogoRepository(mongo_db).remover_hotel(str(hotel_id))
    return None
