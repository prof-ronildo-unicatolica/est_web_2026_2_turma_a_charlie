from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.interacao import Reserva
from app.repositories.catalogo_repository import CatalogoRepository


class BuscaService:
    """Regras de negócio da busca pública de hotéis."""

    def __init__(self, mongo_db: AsyncIOMotorDatabase, db: Session):
        self.repository = CatalogoRepository(mongo_db)
        self.db = db

    async def buscar_hoteis(
        self,
        cidade_id: str | None = None,
        estrelas: int | None = None,
        adultos: int = 1,
        criancas: int = 0,
        checkin: date | None = None,
        checkout: date | None = None,
    ) -> list[dict]:
        filtros = {}
        if cidade_id:
            filtros["cidade_id"] = cidade_id
        if estrelas is not None:
            filtros["categoria_estrelas"] = estrelas

        capacidade = {"max_adultos": {"$gte": adultos}}
        if criancas > 0:
            capacidade["max_criancas"] = {"$gte": criancas}
        filtros["quartos"] = {"$elemMatch": capacidade}

        hoteis = await self.repository.buscar(filtros)
        if not checkin or not checkout:
            return hoteis

        quartos_ids = [
            UUID(quarto["quarto_id"])
            for hotel in hoteis
            for quarto in hotel.get("quartos", [])
            if quarto.get("quarto_id")
        ]
        ocupados = set()
        if quartos_ids:
            reservas = self.db.query(Reserva.quarto_id).filter(
                Reserva.quarto_id.in_(quartos_ids),
                or_(
                    Reserva.status == "confirmada",
                    and_(Reserva.status == "pendente", Reserva.criada_em >= datetime.now(timezone.utc) - timedelta(minutes=30)),
                ),
                Reserva.data_checkin < checkout,
                Reserva.data_checkout > checkin,
            ).all()
            ocupados = {str(item[0]) for item in reservas}

        resultados = []
        for hotel in hoteis:
            quartos_disponiveis = [
                quarto for quarto in hotel.get("quartos", [])
                if quarto.get("quarto_id") not in ocupados
                and quarto.get("max_adultos", 0) >= adultos
                and quarto.get("max_criancas", 0) >= criancas
            ]
            if quartos_disponiveis:
                hotel["quartos"] = quartos_disponiveis
                resultados.append(hotel)
        return resultados
