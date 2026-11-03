import uuid

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db, get_mongo_db
from app.mensagens import QUARTO_NAO_ENCONTRADO
from app.schemas.quarto import (
    QuartoCreateSchema,
    QuartoResponseSchema,
    QuartoUpdateSchema,
)
from app.services.quarto_service import QuartoService

router = APIRouter()


@router.post(
    "/quartos",
    response_model=QuartoResponseSchema,
    status_code=201,
)
async def criar_quarto(
    payload: QuartoCreateSchema,
    db: Session = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db, mongo_db)

    try:
        return await service.create(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível criar o quarto.",
        ) from exc


@router.get(
    "/quartos",
    response_model=list[QuartoResponseSchema],
)
def listar_quartos(db: Session = Depends(get_db)):
    service = QuartoService(db, get_mongo_db())
    return service.list()


@router.get(
    "/quartos/{quarto_id}",
    response_model=QuartoResponseSchema,
)
def buscar_quarto(
    quarto_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = QuartoService(db, get_mongo_db())
    quarto = service.get_by_id(quarto_id)

    if not quarto:
        raise HTTPException(
            status_code=404,
            detail=QUARTO_NAO_ENCONTRADO,
        )

    return quarto


@router.put(
    "/quartos/{quarto_id}",
    response_model=QuartoResponseSchema,
)
async def atualizar_quarto(
    quarto_id: uuid.UUID,
    payload: QuartoUpdateSchema,
    db: Session = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db, mongo_db)
    quarto = await service.update(quarto_id, payload)

    if not quarto:
        raise HTTPException(
            status_code=404,
            detail=QUARTO_NAO_ENCONTRADO,
        )

    return quarto


@router.delete(
    "/quartos/{quarto_id}",
    status_code=204,
)
async def deletar_quarto(
    quarto_id: uuid.UUID,
    db: Session = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db, mongo_db)
    quarto = await service.delete(quarto_id)

    if not quarto:
        raise HTTPException(
            status_code=404,
            detail=QUARTO_NAO_ENCONTRADO,
        )

    return None