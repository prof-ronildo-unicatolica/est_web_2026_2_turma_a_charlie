import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.hotel import Cidade, Hotel
from app.schemas.cidade import CidadeCreate, CidadePublic, CidadeUpdate
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
    _admin=Depends(get_current_admin),
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


@router.patch("/{cidade_id}", response_model=CidadePublic)
def atualizar_cidade(
    cidade_id: uuid.UUID,
    payload: CidadeUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    cidade = db.query(Cidade).filter(Cidade.id == cidade_id).first()
    if not cidade:
        raise HTTPException(status_code=404, detail="Cidade não encontrada.")

    dados = payload.model_dump(exclude_unset=True)
    if not dados or any(valor is None for valor in dados.values()):
        raise HTTPException(status_code=422, detail="Informe campos válidos para atualização.")

    if "nome" in dados:
        nome = dados["nome"].strip()
        if len(nome) < 2:
            raise HTTPException(status_code=422, detail="Informe um nome válido.")
        duplicada = db.query(Cidade).filter(Cidade.nome == nome, Cidade.id != cidade_id).first()
        if duplicada:
            raise HTTPException(status_code=409, detail="Já existe uma cidade com esse nome.")
        cidade.nome = nome

    if "estado" in dados:
        cidade.estado = dados["estado"].strip().upper()

    db.commit()
    db.refresh(cidade)
    return cidade


@router.delete("/{cidade_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cidade(
    cidade_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    cidade = db.query(Cidade).filter(Cidade.id == cidade_id).first()
    if not cidade:
        raise HTTPException(status_code=404, detail="Cidade não encontrada.")
    possui_hoteis = db.query(Hotel).filter(Hotel.cidade_id == cidade_id).first()
    if possui_hoteis:
        raise HTTPException(status_code=409, detail="Não é possível excluir uma cidade que possui hotéis cadastrados.")
    db.delete(cidade)
    db.commit()
    return None
