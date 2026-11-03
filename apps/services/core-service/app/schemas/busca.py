from pydantic import BaseModel, Field


class HotelBuscaResponse(BaseModel):
    """Hotel retornado pela busca pública."""

    hotel_id: str
    nome: str
    categoria_estrelas: int
    cidade_id: str
    cidade_nome: str
    cidade_estado: str
    quartos: list[dict]


class HotelBuscaFiltros(BaseModel):
    """Filtros disponíveis para busca de hotéis."""

    cidade_id: str | None = None
    estrelas: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )