from sqlalchemy.orm import Session

from app.models.comodidade import Comodidade
from app.repositories.comodidade_repository import ComodidadeRepository


class ComodidadeService:
    def __init__(self, db: Session):
        self.repository = ComodidadeRepository(db)

    def create(self, nome: str) -> Comodidade:
        return self.repository.create(nome)

    def list(self) -> list[Comodidade]:
        return self.repository.list()

    def get_by_id(self, comodidade_id: int) -> Comodidade | None:
        return self.repository.get_by_id(comodidade_id)

    def get_by_nome(self, nome: str) -> Comodidade | None:
        return self.repository.get_by_nome(nome)

    def update(self, comodidade: Comodidade, nome: str) -> Comodidade:
        return self.repository.update(comodidade, nome)

    def delete(self, comodidade: Comodidade) -> None:
        self.repository.delete(comodidade)