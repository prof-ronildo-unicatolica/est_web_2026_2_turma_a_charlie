from motor.motor_asyncio import AsyncIOMotorDatabase


class CatalogoRepository:
    """Acesso ao catálogo de hotéis no MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["catalogo_hoteis"]

    async def salvar_hotel(self, hotel: dict) -> None:
        await self.collection.update_one(
            {"hotel_id": hotel["hotel_id"]},
            {"$set": hotel},
            upsert=True,
        )

    async def listar_hoteis(self) -> list[dict]:
        cursor = self.collection.find(
            {},
            {"_id": 0},
        )
        return await cursor.to_list(length=None)

    async def buscar(self, filtros: dict) -> list[dict]:
        cursor = self.collection.find(
            filtros,
            {"_id": 0},
        )
        return await cursor.to_list(length=None)

    async def buscar_por_cidade(self, cidade_id: str) -> list[dict]:
        cursor = self.collection.find(
            {"cidade_id": cidade_id},
            {"_id": 0},
        )
        return await cursor.to_list(length=None)

    async def remover_hotel(self, hotel_id: str) -> None:
        await self.collection.delete_one(
            {"hotel_id": hotel_id},
        )
