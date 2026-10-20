from typing import List

from sqlalchemy.orm import Session, joinedload

from app.models.comodidade import Comodidade
from app.models.hotel import Cidade, Hotel


class CidadeRepository:
    """Acesso ao banco para Cidade. Sem regras de negocio ou HTTPException."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nome: str, estado: str) -> Cidade:
        cidade = Cidade(
            nome=nome,
            estado=estado,
        )
        self.db.add(cidade)
        self.db.commit()
        self.db.refresh(cidade)
        return cidade

    def list(self) -> List[Cidade]:
        return self.db.query(Cidade).order_by(Cidade.nome).all()

    def get_by_id(self, cidade_id) -> Cidade | None:
        return (
            self.db.query(Cidade)
            .filter(Cidade.id == cidade_id)
            .first()
        )

    def get_by_nome(self, nome: str) -> Cidade | None:
        return (
            self.db.query(Cidade)
            .filter(Cidade.nome == nome)
            .first()
        )


class HotelRepository:
    """Acesso ao banco para Hotel com carregamento ansioso."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        nome: str,
        cidade_id,
        categoria_estrelas: int,
        comodidades: List[Comodidade] | None = None,
    ) -> Hotel:
        hotel = Hotel(
            nome=nome,
            cidade_id=cidade_id,
            categoria_estrelas=categoria_estrelas,
        )

        if comodidades:
            hotel.comodidades = comodidades

        self.db.add(hotel)
        self.db.commit()
        self.db.refresh(hotel)

        return hotel

    def list(self) -> List[Hotel]:
        return (
            self.db.query(Hotel)
            .options(
                joinedload(Hotel.cidade),
                joinedload(Hotel.quartos),
                joinedload(Hotel.comodidades),
            )
            .order_by(Hotel.nome)
            .all()
        )

    def list_by_cidade(self, cidade_id) -> List[Hotel]:
        return (
            self.db.query(Hotel)
            .options(
                joinedload(Hotel.cidade),
                joinedload(Hotel.quartos),
                joinedload(Hotel.comodidades),
            )
            .filter(Hotel.cidade_id == cidade_id)
            .order_by(Hotel.nome)
            .all()
        )

    def get_by_id(self, hotel_id) -> Hotel | None:
        return (
            self.db.query(Hotel)
            .options(
                joinedload(Hotel.cidade),
                joinedload(Hotel.quartos),
                joinedload(Hotel.comodidades),
            )
            .filter(Hotel.id == hotel_id)
            .first()
        )

    def get_comodidades_by_ids(
        self,
        comodidade_ids: List[int],
    ) -> List[Comodidade]:
        if not comodidade_ids:
            return []

        return (
            self.db.query(Comodidade)
            .filter(Comodidade.id.in_(comodidade_ids))
            .all()
        )