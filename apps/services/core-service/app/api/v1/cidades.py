from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.cidade import CidadeCreate, CidadePublic
from app.services.hotel_service import CidadeService


router = APIRouter(
    prefix="/cidades",
    tags=["Cidades"],
)


@router.post(
    "",
    response_model=CidadePublic,
    status_code=status.HTTP_201_CREATED,
)
def criar_cidade(
    payload: CidadeCreate,
    db: Session = Depends(get_db),
):
    service = CidadeService(db)

    nome = payload.nome.strip()

    if not nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O nome da cidade não pode ser vazio.",
        )

    if service.get_by_nome(nome):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cidade já cadastrada.",
        )

    payload.nome = nome

    return service.create(payload)


@router.get(
    "",
    response_model=list[CidadePublic],
)
def listar_cidades(
    db: Session = Depends(get_db),
):
    service = CidadeService(db)
    return service.list()