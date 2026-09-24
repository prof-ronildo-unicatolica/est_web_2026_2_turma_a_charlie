import uuid

from pydantic import BaseModel, ConfigDict


class CidadeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str
    estado: str


class CidadeCreate(CidadeBase):
    pass


class CidadePublic(CidadeBase):
    id: uuid.UUID