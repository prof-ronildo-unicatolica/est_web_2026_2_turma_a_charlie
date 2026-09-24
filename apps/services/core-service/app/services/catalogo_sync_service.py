from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.catalogo_repository import CatalogoRepository
from app.repositories.hotel_repository import HotelRepository


class CatalogoSyncService:
    """Sincroniza hotéis do PostgreSQL para o catálogo no MongoDB."""

    def __init__(self, db: Session, mongo_db):
        self.hotel_repository = HotelRepository(db)
        self.catalogo_repository = CatalogoRepository(mongo_db)

    async def sincronizar_hotel(self, hotel_id) -> None:
        hotel = self.hotel_repository.get_by_id(hotel_id)

        if not hotel:
            await self.catalogo_repository.remover_hotel(
                str(hotel_id),
            )
            return

        documento = {
            "hotel_id": str(hotel.id),
            "nome": hotel.nome,
            "categoria_estrelas": hotel.categoria_estrelas,
            "cidade_id": str(hotel.cidade.id),
            "cidade_nome": hotel.cidade.nome,
            "cidade_estado": hotel.cidade.estado,
            "quartos": [
                {
                    "quarto_id": str(quarto.id),
                    "tipo": quarto.tipo,
                    "preco_diaria": float(
                        quarto.preco_diaria
                        if isinstance(quarto.preco_diaria, Decimal)
                        else quarto.preco_diaria
                    ),
                    "max_adultos": quarto.max_adultos,
                    "max_criancas": quarto.max_criancas,
                }
                for quarto in hotel.quartos
            ],
        }

        await self.catalogo_repository.salvar_hotel(documento)