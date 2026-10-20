import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db, get_mongo_db
from app.mensagens import HOTEL_NAO_ENCONTRADO
from app.schemas.cidade import CidadeCreate, CidadePublic
from app.schemas.hotel import HotelCreateSchema, HotelResponseSchema
from app.services.hotel_service import CidadeService, HotelService

router = APIRouter()


@router.post(
    "/cidades",
    response_model=CidadePublic,
    status_code=201,
)
def criar_cidade(
    payload: CidadeCreate,
    db: Session = Depends(get_db),
):
    service = CidadeService(db)

    cidade_existente = service.get_by_nome(payload.nome)

    if cidade_existente:
        raise HTTPException(
            status_code=409,
            detail="Cidade ja cadastrada.",
        )

    return service.create(payload)


@router.get(
    "/cidades",
    response_model=list[CidadePublic],
)
def listar_cidades(
    db: Session = Depends(get_db),
):
    service = CidadeService(db)
    return service.list()


@router.post(
    "/hoteis",
    response_model=HotelResponseSchema,
    status_code=201,
)
async def criar_hotel(
    payload: HotelCreateSchema,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    service = HotelService(db, mongo_db)

    cidade = CidadeService(db).get_by_id(payload.cidade_id)

    if not cidade:
        raise HTTPException(
            status_code=404,
            detail="Cidade nao encontrada.",
        )

    return await service.create(payload)


@router.get(
    "/hoteis",
    response_model=list[HotelResponseSchema],
)
def listar_hoteis(
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    service = HotelService(db, mongo_db)
    return service.list()


@router.get(
    "/hoteis/{hotel_id}",
    response_model=HotelResponseSchema,
)
def buscar_hotel(
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
    cidade_service = CidadeService(db)

    cidade = cidade_service.get_by_id(cidade_id)

    if not cidade:
        raise HTTPException(
            status_code=404,
            detail="Cidade nao encontrada.",
        )

    hotel_service = HotelService(db, mongo_db)

    return hotel_service.list_by_cidade(cidade_id)