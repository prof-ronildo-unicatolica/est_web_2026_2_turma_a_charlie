from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.schemas.comodidade import (
    ComodidadeCreate,
    ComodidadePublic,
    ComodidadeUpdate,
)
from app.services.comodidade_service import ComodidadeService

router = APIRouter(prefix="/comodidades", tags=["Comodidades"])


@router.post(
    "",
    response_model=ComodidadePublic,
    status_code=status.HTTP_201_CREATED,
)
def criar_comodidade(
    payload: ComodidadeCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    service = ComodidadeService(db)
    nome = payload.nome.strip()

    if not nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O nome da comodidade não pode ser vazio.",
        )

    if service.get_by_nome(nome):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma comodidade com esse nome.",
        )

    return service.create(nome)


@router.get("", response_model=list[ComodidadePublic])
def listar_comodidades(db: Session = Depends(get_db)):
    return ComodidadeService(db).list()


@router.put("/{comodidade_id}", response_model=ComodidadePublic)
def atualizar_comodidade(
    comodidade_id: int,
    payload: ComodidadeUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    service = ComodidadeService(db)

    comodidade = service.get_by_id(comodidade_id)

    if not comodidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comodidade não encontrada.",
        )

    nome = payload.nome.strip()

    if not nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O nome da comodidade não pode ser vazio.",
        )

    existente = service.get_by_nome(nome)

    if existente and existente.id != comodidade_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma comodidade com esse nome.",
        )

    return service.update(comodidade, nome)


@router.delete(
    "/{comodidade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_comodidade(
    comodidade_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    service = ComodidadeService(db)

    comodidade = service.get_by_id(comodidade_id)

    if not comodidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comodidade não encontrada.",
        )

    service.delete(comodidade)