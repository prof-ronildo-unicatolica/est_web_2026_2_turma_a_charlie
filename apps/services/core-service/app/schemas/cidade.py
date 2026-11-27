import uuid

from pydantic import BaseModel, Field


class CidadeBase(BaseModel):
    nome: str
    estado: str


class CidadeCreate(CidadeBase):
    pass


class CidadeUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    estado: str | None = Field(default=None, min_length=2, max_length=2)


class CidadePublic(CidadeBase):
    id: uuid.UUID
