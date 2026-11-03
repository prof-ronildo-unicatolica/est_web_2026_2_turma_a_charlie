from fastapi import APIRouter, Depends, Query

from app.core.database import get_mongo_db
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
    mongo_db=Depends(get_mongo_db),
):
    service = BuscaService(mongo_db)

    return await service.buscar_hoteis(
        cidade_id=cidade_id,
        estrelas=estrelas,
    )