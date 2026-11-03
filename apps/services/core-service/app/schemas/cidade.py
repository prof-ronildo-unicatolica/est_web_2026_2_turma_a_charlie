import uuid

from pydantic import BaseModel, ConfigDict, Field


class CidadeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(min_length=1, max_length=100)
    estado: str = Field(min_length=2, max_length=2)


class CidadeCreate(CidadeBase):
    pass


class CidadePublic(CidadeBase):
    id: uuid.UUID