from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comodidade import Comodidade


class ComodidadeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, nome: str) -> Comodidade:
        comodidade = Comodidade(nome=nome)
        self.db.add(comodidade)
        self.db.commit()
        self.db.refresh(comodidade)
        return comodidade

    def list(self) -> list[Comodidade]:
        return list(
            self.db.scalars(
                select(Comodidade).order_by(Comodidade.nome)
            ).all()
        )

    def get_by_id(self, comodidade_id: int) -> Comodidade | None:
        return self.db.get(Comodidade, comodidade_id)

    def get_by_nome(self, nome: str) -> Comodidade | None:
        return self.db.scalar(
            select(Comodidade).where(Comodidade.nome == nome)
        )

    def update(self, comodidade: Comodidade, nome: str) -> Comodidade:
        comodidade.nome = nome
        self.db.commit()
        self.db.refresh(comodidade)
        return comodidade

    def delete(self, comodidade: Comodidade) -> None:
        self.db.delete(comodidade)
        self.db.commit()