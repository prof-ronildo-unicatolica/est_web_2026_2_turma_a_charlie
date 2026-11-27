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
    adultos: int = Field(default=1, ge=1, le=20)
    criancas: int = Field(default=0, ge=0, le=20)