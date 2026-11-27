
import uuid

from pydantic import BaseModel, ConfigDict, Field


class CidadeBase(BaseModel):
    nome: str
    estado: str


class CidadeCreate(CidadeBase):
    pass


class CidadeUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    estado: str | None = Field(default=None, min_length=2, max_length=2)


class CidadePublic(CidadeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
