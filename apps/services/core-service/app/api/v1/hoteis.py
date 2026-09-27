import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db, get_mongo_db
from app.models.hotel import Cidade
from app.schemas.hotel import HotelCreateSchema, HotelResponseSchema
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
def criar_hotel(
    payload: HotelCreateSchema,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
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

    return service.create(payload)


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel não encontrado.",
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