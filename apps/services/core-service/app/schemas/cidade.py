import uuid

from pydantic import BaseModel, ConfigDict, Field


class CidadeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(min_length=1, max_length=100)


class CidadeCreate(CidadeBase):
    pass


class CidadePublic(CidadeBase):
    id: uuid.UUID


class CidadeCreateSchema(BaseModel):
    """Dados recebidos para criar uma cidade."""

    nome: str = Field(min_length=1, max_length=100)


class CidadeResponseSchema(BaseModel):
    """Dados devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str