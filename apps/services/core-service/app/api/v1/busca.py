from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db, get_mongo_db
from app.schemas.busca import HotelBuscaResponse
from app.services.busca_service import BuscaService

router = APIRouter()


@router.get(
    "/busca/hoteis",
    response_model=list[HotelBuscaResponse],
)
async def buscar_hoteis(
    cidade_id: str | None = Query(default=None),
    estrelas: int | None = Query(default=None, ge=1, le=5),
    adultos: int = Query(default=1, ge=1, le=20),
    criancas: int = Query(default=0, ge=0, le=20),
    checkin: date | None = Query(default=None),
    checkout: date | None = Query(default=None),
    mongo_db=Depends(get_mongo_db),
    db: Session = Depends(get_db),
):
    if (checkin is None) != (checkout is None):
        raise HTTPException(status_code=422, detail="Informe check-in e check-out.")
    if checkin and checkout and checkout <= checkin:
        raise HTTPException(status_code=422, detail="O check-out deve ser posterior ao check-in.")

    service = BuscaService(mongo_db, db)
    return await service.buscar_hoteis(
        cidade_id=cidade_id,
        estrelas=estrelas,
        adultos=adultos,
        criancas=criancas,
        checkin=checkin,
        checkout=checkout,
    )
