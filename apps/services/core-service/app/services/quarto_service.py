from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.repositories.quarto_repository import QuartoRepository
from app.services.catalogo_sync_service import CatalogoSyncService


class QuartoService:
    def __init__(
        self,
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
    ):
        self.repository = QuartoRepository(db)
        self.catalogo_sync = CatalogoSyncService(db, mongo_db)

    async def create(self, payload):
        quarto = self.repository.create(
            hotel_id=payload.hotel_id,
            tipo=payload.tipo,
            preco_diaria=payload.preco_diaria,
            max_adultos=payload.max_adultos,
            max_criancas=payload.max_criancas,
        )

        await self.catalogo_sync.sincronizar_hotel(quarto.hotel_id)

        return quarto

    def list(self):
        return self.repository.list()

    def get_by_id(self, quarto_id):
        return self.repository.get_by_id(quarto_id)

    async def update(self, quarto_id, payload):
        quarto = self.repository.get_by_id(quarto_id)

        if not quarto:
            return None

        dados = payload.model_dump(exclude_unset=True)

        quarto = self.repository.update(quarto, dados)

        await self.catalogo_sync.sincronizar_hotel(quarto.hotel_id)

        return quarto

    async def delete(self, quarto_id):
        quarto = self.repository.get_by_id(quarto_id)

        if not quarto:
            return None

        hotel_id = quarto.hotel_id

        self.repository.delete(quarto)

        await self.catalogo_sync.sincronizar_hotel(hotel_id)

        return quarto