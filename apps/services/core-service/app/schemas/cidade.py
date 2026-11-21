import uuid

from pydantic import BaseModel


class CidadeBase(BaseModel):
    nome: str
    estado: str


class CidadeCreate(CidadeBase):
    pass


class CidadePublic(CidadeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
