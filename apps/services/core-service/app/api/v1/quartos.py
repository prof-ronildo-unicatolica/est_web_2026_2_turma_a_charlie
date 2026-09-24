import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.services.quarto_service import QuartoService
from app.schemas.quarto import (
    QuartoCreateSchema,
    QuartoResponseSchema,
    QuartoUpdateSchema,
)

router = APIRouter()


@router.post(
    "/quartos",
    response_model=QuartoResponseSchema,
    status_code=201,
)
def criar_quarto(
    payload: QuartoCreateSchema,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db)

    try:
        return service.create(payload)
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
    service = QuartoService(db)
    return service.list()


@router.get(
    "/quartos/{quarto_id}",
    response_model=QuartoResponseSchema,
)
def buscar_quarto(
    quarto_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = QuartoService(db)
    quarto = service.get_by_id(quarto_id)

    if not quarto:
        raise HTTPException(
            status_code=404,
            detail="Quarto não encontrado.",
        )

    return quarto


@router.put(
    "/quartos/{quarto_id}",
    response_model=QuartoResponseSchema,
)
def atualizar_quarto(
    quarto_id: uuid.UUID,
    payload: QuartoUpdateSchema,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db)
    quarto = service.update(quarto_id, payload)

    if not quarto:
        raise HTTPException(
            status_code=404,
            detail="Quarto não encontrado.",
        )

    return quarto


@router.delete(
    "/quartos/{quarto_id}",
    status_code=204,
)
def deletar_quarto(
    quarto_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db)
    quarto = service.delete(quarto_id)

    if not quarto:
        raise HTTPException(
            status_code=404,
            detail="Quarto não encontrado.",
        )

    return None