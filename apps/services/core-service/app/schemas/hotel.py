import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cidade import CidadePublic


class HotelCreateSchema(BaseModel):
    """Dados recebidos para criar um hotel."""

    nome: str = Field(min_length=1, max_length=100)
    cidade_id: uuid.UUID


class HotelResponseSchema(BaseModel):
    """Dados devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    cidade: CidadePublic