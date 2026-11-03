from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.catalogo_repository import CatalogoRepository


class CatalogoService:
    """Regras de negócio do catálogo de hotéis."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.repository = CatalogoRepository(db)

    async def salvar_hotel(self, hotel: dict) -> None:
        await self.repository.salvar_hotel(hotel)

    async def listar_hoteis(self) -> list[dict]:
        return await self.repository.listar_hoteis()

    async def buscar_por_cidade(self, cidade_id: str) -> list[dict]:
        return await self.repository.buscar_por_cidade(cidade_id)

    async def remover_hotel(self, hotel_id: str) -> None:
        await self.repository.remover_hotel(hotel_id)