import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cidade import CidadePublic
from app.schemas.comodidade import ComodidadePublic


class HotelCreateSchema(BaseModel):
    """Dados recebidos para criar um hotel."""

    nome: str = Field(min_length=1, max_length=100)
    cidade_id: uuid.UUID
    categoria_estrelas: int = Field(ge=1, le=5)
    comodidade_ids: list[int] = Field(default_factory=list)


class HotelResponseSchema(BaseModel):
    """Dados devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    categoria_estrelas: int
    cidade: CidadePublic
    comodidades: list[ComodidadePublic] = []