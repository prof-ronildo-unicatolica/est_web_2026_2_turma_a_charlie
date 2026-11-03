import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QuartoCreateSchema(BaseModel):
    """Dados recebidos para criar um quarto."""

    hotel_id: uuid.UUID
    tipo: str = Field(min_length=1, max_length=50)
    preco_diaria: Decimal = Field(gt=0)
    max_adultos: int = Field(ge=1)
    max_criancas: int = Field(ge=0)


class QuartoUpdateSchema(BaseModel):
    """Dados recebidos para atualizar um quarto."""

    tipo: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    preco_diaria: Decimal | None = Field(
        default=None,
        gt=0,
    )
    max_adultos: int | None = Field(
        default=None,
        ge=1,
    )
    max_criancas: int | None = Field(
        default=None,
        ge=0,
    )
    

class QuartoResponseSchema(BaseModel):
    """Dados devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hotel_id: uuid.UUID
    tipo: str
    preco_diaria: Decimal
    max_adultos: int
    max_criancas: int
    