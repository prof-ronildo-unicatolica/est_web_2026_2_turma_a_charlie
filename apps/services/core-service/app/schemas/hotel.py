import uuid

from pydantic import BaseModel, ConfigDict, Field


class CidadeCreateSchema(BaseModel):
    """O que o cliente envia em POST /cidades."""

    nome: str = Field(min_length=1, max_length=100)


class CidadeResponseSchema(BaseModel):
    """O que a API devolve."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str