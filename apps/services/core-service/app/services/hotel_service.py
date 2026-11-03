from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.repositories.hotel_repository import CidadeRepository, HotelRepository
from app.services.catalogo_sync_service import CatalogoSyncService


class CidadeService:
    """Regras de negocio de Cidade."""

    def __init__(self, db: Session):
        self.repository = CidadeRepository(db)

    def create(self, payload):
        return self.repository.create(
            nome=payload.nome,
            estado=payload.estado,
        )

    def list(self):
        return self.repository.list()

    def get_by_id(self, cidade_id):
        return self.repository.get_by_id(cidade_id)

    def get_by_nome(self, nome):
        return self.repository.get_by_nome(nome)


class HotelService:
    """Regras de negocio de Hotel."""

    def __init__(
        self,
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
    ):
        self.repository = HotelRepository(db)
        self.catalogo_sync = CatalogoSyncService(db, mongo_db)

    async def create(self, payload):
        comodidades = self.repository.get_comodidades_by_ids(
            payload.comodidade_ids
        )

        ids_encontradas = {comodidade.id for comodidade in comodidades}
        ids_recebidas = set(payload.comodidade_ids)

        ids_invalidas = ids_recebidas - ids_encontradas

        if ids_invalidas:
            raise ValueError(
                f"Comodidades não encontradas: {sorted(ids_invalidas)}"
            )

        hotel = self.repository.create(
            nome=payload.nome,
            cidade_id=payload.cidade_id,
            categoria_estrelas=payload.categoria_estrelas,
            comodidades=comodidades,
        )

        await self.catalogo_sync.sincronizar_hotel(hotel.id)

        return hotel

    def list(self):
        return self.repository.list()

    def list_by_cidade(self, cidade_id):
        return self.repository.list_by_cidade(cidade_id)

    def get_by_id(self, hotel_id):
        return self.repository.get_by_id(hotel_id)